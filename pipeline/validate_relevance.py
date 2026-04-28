"""Validate that matched PubMed articles are actually about the specific device.

Uses an LLM (Claude via Anthropic API) to review each paper title and determine
if it's genuinely about the FDA device or a false positive match.

Usage:
    # Requires ANTHROPIC_API_KEY in .env
    python validate_relevance.py data/enriched_final.json

    # Dry run - just show what would be validated
    python validate_relevance.py data/enriched_final.json --dry-run

    # Only validate devices with >10 direct pubs (most likely contaminated)
    python validate_relevance.py data/enriched_final.json --min-pubs 10
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def validate_with_llm(device_name: str, company: str, specialty: str, articles: list[dict]) -> list[dict]:
    """Ask Claude to classify each article as relevant or not.

    Returns the same articles list with a 'relevance' field added:
      - "relevant": paper is about this specific device
      - "maybe": paper is related but not specifically about this device
      - "irrelevant": paper is not about this device at all
    """
    if not ANTHROPIC_API_KEY:
        # No API key - fall back to heuristic validation
        return _heuristic_validate(device_name, company, articles)

    import httpx
    from enrich_pubmed import fetch_abstracts

    # Fetch abstracts for all articles (critical: PubMed matched on abstracts
    # but without them the LLM can only see titles, causing over-rejection)
    all_pmids = [a.get("pmid", "") for a in articles if a.get("pmid")]
    abstracts = {}
    if all_pmids:
        # Batch abstract fetches in groups of 100
        for ab_i in range(0, len(all_pmids), 100):
            ab_batch = all_pmids[ab_i:ab_i+100]
            abstracts.update(fetch_abstracts(ab_batch))
            time.sleep(0.2)

    # Batch articles into groups of 10 (smaller batches since we include abstracts)
    validated = []
    for i in range(0, len(articles), 10):
        batch = articles[i:i+10]
        entries = []
        for j, a in enumerate(batch):
            pmid = a.get("pmid", "")
            abstract = abstracts.get(pmid, "")
            if abstract:
                entries.append(f"{j+1}. TITLE: {a['title']}\n   ABSTRACT: {abstract[:500]}")
            else:
                entries.append(f"{j+1}. TITLE: {a['title']}")
        article_text = "\n\n".join(entries)

        prompt = f"""You are validating whether PubMed articles are about a specific FDA-cleared medical device.

Device: {device_name}
Company: {company}
Specialty: {specialty}

For each article below (title and abstract), respond with ONLY the number and one of: RELEVANT, MAYBE, IRRELEVANT
- RELEVANT: The paper specifically studies, evaluates, or validates this device (mentions it by name or clearly refers to it)
- MAYBE: The paper is about the same technology area or company but does not clearly reference this specific device
- IRRELEVANT: The paper has nothing to do with this device (coincidental word match)

Articles:
{article_text}

Respond in format:
1. RELEVANT
2. IRRELEVANT
3. MAYBE
..."""

        try:
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()["content"][0]["text"]

            # Parse response
            for j, article in enumerate(batch):
                line_num = j + 1
                for line in result.strip().split("\n"):
                    if line.strip().startswith(f"{line_num}."):
                        upper = line.upper()
                        if "IRRELEVANT" in upper:
                            article["relevance"] = "irrelevant"
                        elif "MAYBE" in upper:
                            article["relevance"] = "maybe"
                        else:
                            article["relevance"] = "relevant"
                        break
                else:
                    article["relevance"] = "unknown"

                validated.append(article)

            time.sleep(0.5)  # Rate limit

        except Exception as e:
            print(f"    LLM validation error: {e}", flush=True)
            for article in batch:
                article["relevance"] = "unknown"
                validated.append(article)

    return validated


def _heuristic_validate(device_name: str, company: str, articles: list[dict]) -> list[dict]:
    """Fallback validation without LLM. Uses simple title matching."""
    import re
    clean = re.sub(r"\s*\(v?[\d.x]+\)\s*", " ", device_name).strip().lower()
    company_short = company.split(",")[0].strip().lower() if company else ""

    for article in articles:
        title = article.get("title", "").lower()
        # If the full device name appears in the title, likely relevant
        if clean in title:
            article["relevance"] = "relevant"
        # If company name appears, maybe relevant
        elif company_short and company_short in title:
            article["relevance"] = "maybe"
        else:
            article["relevance"] = "maybe"

    return articles


def run_validation(data_path: str, min_pubs: int = 0, dry_run: bool = False):
    with open(data_path) as f:
        devices = json.load(f)

    total_articles = 0
    total_irrelevant = 0
    devices_checked = 0

    for i, device in enumerate(devices):
        evidence = device.get("evidence", [])
        direct = [e for e in evidence if e.get("match_tier") == "direct"]
        n_direct = len(direct)

        if n_direct <= min_pubs:
            continue

        name = device.get("device_name", "")
        company = device.get("company", "")
        specialty = device.get("specialty_panel", "")

        if dry_run:
            print(f"  Would validate: {name} ({n_direct} direct articles)")
            devices_checked += 1
            continue

        print(f"  [{i+1}/{len(devices)}] {name} ({n_direct} articles)", flush=True)

        validated = validate_with_llm(name, company, specialty, direct)

        # Replace direct evidence with validated versions
        company_evidence = [e for e in evidence if e.get("match_tier") != "direct"]
        device["evidence"] = validated + company_evidence

        # Remove irrelevant articles
        irrelevant = sum(1 for a in validated if a.get("relevance") == "irrelevant")
        total_irrelevant += irrelevant
        total_articles += n_direct
        devices_checked += 1

        if irrelevant > 0:
            print(f"    Removed {irrelevant}/{n_direct} irrelevant articles")

    if dry_run:
        print(f"\nWould validate {devices_checked} devices")
        return

    # Remove irrelevant articles and recompute scores
    from score import compute_score
    for device in devices:
        evidence = device.get("evidence", [])
        # Keep relevant and maybe, remove only irrelevant
        # Maybe articles are kept in the data but tagged for the dashboard
        cleaned = [e for e in evidence if e.get("relevance") != "irrelevant"]
        device["evidence"] = cleaned

        # Recompute score
        device["score"] = compute_score(
            cleaned,
            device.get("safety_events", []),
            device.get("recalls", []),
            device.get("trials", []),
        )

    # Save
    out_path = Path(data_path)
    with open(out_path, "w") as f:
        json.dump(devices, f, indent=2, default=str)

    print(f"\nValidation complete:")
    print(f"  Devices checked: {devices_checked}")
    print(f"  Total articles reviewed: {total_articles}")
    print(f"  Irrelevant removed: {total_irrelevant}")
    print(f"  Saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_relevance.py <enriched_json> [--dry-run] [--min-pubs N]")
        sys.exit(1)

    data_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    min_pubs = 0
    for j, arg in enumerate(sys.argv):
        if arg == "--min-pubs" and j + 1 < len(sys.argv):
            min_pubs = int(sys.argv[j + 1])

    run_validation(data_path, min_pubs=min_pubs, dry_run=dry_run)

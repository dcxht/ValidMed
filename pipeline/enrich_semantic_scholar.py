"""Search Semantic Scholar for evidence not indexed in PubMed.

Semantic Scholar indexes:
  - PubMed (overlap with our primary search)
  - arXiv preprints
  - Conference proceedings (RSNA, SPIE, MICCAI, IEEE, ACM)
  - medRxiv/bioRxiv preprints
  - Springer, Elsevier, Wiley, etc.

This catches conference papers, preprints, and non-PubMed journals.
"""

import re
import time

import httpx

SS_BASE = "https://api.semanticscholar.org/graph/v1"
SS_DELAY = 1.1  # Free tier: ~1 req/sec


def _normalize(text: str) -> str:
    text = re.sub(r"[™®©\-–—]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def _clean_name(device_name: str) -> str:
    name = re.sub(r"\s*\(v?[\d.x]+\)\s*", " ", device_name)
    name = re.sub(r"\s+v[\d.x]+$", "", name)
    name = re.sub(r"\s*\([A-Z]{1,3}\d+\)\s*$", "", name)
    return name.strip()


def search_semantic_scholar(query: str, max_results: int = 10) -> list[dict]:
    """Search Semantic Scholar. Returns list of paper records."""
    params = {
        "query": query,
        "fields": "title,year,venue,publicationTypes,externalIds,citationCount",
        "limit": max_results,
    }

    for attempt in range(3):
        try:
            resp = httpx.get(f"{SS_BASE}/paper/search", params=params, timeout=30)
            if resp.status_code == 429:
                time.sleep(3 ** attempt)
                continue
            if resp.status_code != 200:
                return []
            resp.raise_for_status()
            break
        except Exception:
            time.sleep(3 ** attempt)
    else:
        return []

    data = resp.json()
    return data.get("data", [])


def enrich_device(device_name: str, company: str, existing_pmids: set[str] = None) -> list[dict]:
    """Find evidence in Semantic Scholar that isn't already in our PubMed results.

    Args:
        device_name: FDA device name
        company: Company name
        existing_pmids: Set of PMIDs already found via PubMed (to deduplicate)
    """
    if existing_pmids is None:
        existing_pmids = set()

    clean = _clean_name(device_name)
    results = []

    # Search for device name
    if len(clean) >= 4:
        papers = search_semantic_scholar(f'"{clean}"')
        time.sleep(SS_DELAY)

        for paper in papers:
            # Skip if we already have this via PubMed
            ext_ids = paper.get("externalIds") or {}
            pmid = ext_ids.get("PubMed")
            if pmid and pmid in existing_pmids:
                continue

            # Verify relevance — device name should appear in title
            title = _normalize(paper.get("title", ""))
            if _normalize(clean) not in title:
                continue

            venue = paper.get("venue", "") or ""
            pub_types = paper.get("publicationTypes") or []

            results.append({
                "title": paper.get("title", ""),
                "year": paper.get("year"),
                "venue": venue,
                "source": "semantic_scholar",
                "is_preprint": _is_preprint(venue, pub_types),
                "is_conference": _is_conference(venue, pub_types),
                "citation_count": paper.get("citationCount", 0),
                "pmid": pmid,
            })

    return results


def _is_preprint(venue: str, pub_types: list) -> bool:
    venue_lower = venue.lower()
    return any(kw in venue_lower for kw in ("arxiv", "medrxiv", "biorxiv", "preprint", "ssrn"))


def _is_conference(venue: str, pub_types: list) -> bool:
    venue_lower = venue.lower()
    conf_keywords = ("rsna", "spie", "miccai", "ieee", "acm", "conference",
                     "proceedings", "symposium", "workshop", "aaai", "neurips")
    return any(kw in venue_lower for kw in conf_keywords) or "Conference" in pub_types


if __name__ == "__main__":
    test_cases = [
        ("Viz LVO", "Viz.ai, Inc."),
        ("Aidoc BriefCase", "Aidoc Medical, Ltd."),
        ("IDx-DR", "Digital Diagnostics Inc."),
    ]

    for name, company in test_cases:
        results = enrich_device(name, company)
        preprints = sum(1 for r in results if r["is_preprint"])
        conferences = sum(1 for r in results if r["is_conference"])
        print(f"\n=== {name} ===")
        print(f"  {len(results)} non-PubMed results ({preprints} preprints, {conferences} conference)")
        for r in results[:3]:
            tag = "preprint" if r["is_preprint"] else ("conf" if r["is_conference"] else "journal")
            print(f"  [{tag}] [{r['year']}] {r['title'][:75]}")

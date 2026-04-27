"""Enrich devices with published evidence from OpenAlex.

Complements PubMed enrichment with citation counts, open-access flags,
and broader coverage of conference papers and preprints.

Search strategy (multi-tier):
  1. Exact device name — high confidence
  2. Company + device name — medium confidence
  3. Company + AI/ML keywords — lower confidence
"""

import re
import time
from typing import Optional

import httpx

from config import PUBMED_DELAY  # reuse as a polite delay baseline

OPENALEX_BASE = "https://api.openalex.org/works"
OPENALEX_MAILTO = "contact@validmed.org"

# Fields we actually need — keeps responses small
_SELECT_FIELDS = ",".join([
    "id",
    "doi",
    "title",
    "publication_year",
    "primary_location",
    "type",
    "cited_by_count",
    "open_access",
    "ids",
])

SKIP_NAMES = {
    "ct", "mri", "ai", "x-ray", "ecg", "ekg",
    "ultrasound", "dose", "software",
}

# OpenAlex type -> venue category mapping
_TYPE_TO_VENUE = {
    "journal-article": "journal",
    "article": "journal",
    "review": "journal",
    "editorial": "journal",
    "letter": "journal",
    "erratum": "journal",
    "proceedings-article": "conference",
    "proceedings": "conference",
    "posted-content": "preprint",
    "preprint": "preprint",
    "book-chapter": "other",
    "book": "other",
    "dissertation": "other",
    "dataset": "other",
    "report": "other",
    "standard": "other",
    "peer-review": "other",
}


# ── helpers ──────────────────────────────────────────────────────────


def _is_searchable(device_name: str) -> bool:
    name = device_name.strip().lower()
    if len(name) < 4:
        return False
    if name in SKIP_NAMES:
        return False
    if re.match(r"^v?\d+(\.\d+)*$", name):
        return False
    return True


def _clean_name(device_name: str) -> str:
    """Remove version numbers and trailing punctuation."""
    name = re.sub(r"\s*\(v?[\d.x]+\)\s*", " ", device_name)
    name = re.sub(r"\s+v[\d.x]+$", "", name)
    name = re.sub(r"\s*\([A-Z]{1,3}\d+\)\s*$", "", name)
    return name.strip()


def _normalize(text: str) -> str:
    text = re.sub(r"[™®©\-–—]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def _get_company_name(company: str) -> str:
    """Extract the meaningful part of a company name."""
    if not company:
        return ""
    name = company.split(",")[0].strip()
    for suffix in (
        " Inc", " LLC", " Ltd", " Corp", " S.A.", " SAS", " BV",
        " GmbH", " Co.", " Medical Systems", " Medical", " Health",
        " Technologies", " Diagnostics",
    ):
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    return name


def _extract_pmid(ids_block: dict) -> Optional[str]:
    """Pull PMID from OpenAlex ids object if present."""
    pmid_url = ids_block.get("pmid", "")
    if pmid_url:
        # Format: "https://pubmed.ncbi.nlm.nih.gov/12345678"
        match = re.search(r"(\d+)$", pmid_url)
        if match:
            return match.group(1)
    return None


def _classify_venue(work: dict) -> str:
    """Tag a work as journal / conference / preprint / other."""
    work_type = (work.get("type") or "").lower()
    venue = _TYPE_TO_VENUE.get(work_type)
    if venue:
        return venue

    # Fall back: inspect the source name for clues
    loc = work.get("primary_location") or {}
    source = loc.get("source") or {}
    source_type = (source.get("type") or "").lower()
    if "journal" in source_type:
        return "journal"
    if "conference" in source_type or "proceedings" in source_type:
        return "conference"
    if "repository" in source_type:
        return "preprint"

    return "other"


def _parse_work(work: dict) -> dict:
    """Convert an OpenAlex work into our standard result dict."""
    loc = work.get("primary_location") or {}
    source_obj = loc.get("source") or {}
    oa = work.get("open_access") or {}
    ids = work.get("ids") or {}

    doi_raw = work.get("doi") or ""
    doi = doi_raw.replace("https://doi.org/", "") if doi_raw else ""

    return {
        "openalex_id": work.get("id", ""),
        "title": work.get("title") or "",
        "year": work.get("publication_year"),
        "venue": source_obj.get("display_name", ""),
        "venue_type": _classify_venue(work),
        "doi": doi,
        "citation_count": work.get("cited_by_count", 0),
        "is_open_access": oa.get("is_oa", False),
        "pmid": _extract_pmid(ids),
        "source": "openalex",
    }


# ── API layer ────────────────────────────────────────────────────────


def _search_openalex(
    query: str,
    *,
    filter_str: str = "",
    max_results: int = 50,
) -> list[dict]:
    """Execute an OpenAlex search with retries.

    Returns a list of parsed work dicts.
    """
    params: dict = {
        "mailto": OPENALEX_MAILTO,
        "per_page": min(max_results, 200),
        "select": _SELECT_FIELDS,
    }

    if filter_str:
        params["filter"] = filter_str
    if query:
        params["search"] = query

    for attempt in range(3):
        try:
            resp = httpx.get(OPENALEX_BASE, params=params, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data = resp.json()
            works = data.get("results", [])
            return [_parse_work(w) for w in works]
        except Exception:
            time.sleep(2 ** attempt)

    return []


# ── main enrichment function ─────────────────────────────────────────


def enrich_device(
    device_name: str,
    company: str,
    existing_pmids: Optional[set[str]] = None,
) -> list[dict]:
    """Multi-tier OpenAlex search for a device.

    Args:
        device_name: The FDA-listed device name.
        company: The manufacturer / submitter company.
        existing_pmids: Set of PMIDs already collected from PubMed.
            Any OpenAlex result matching these is dropped to avoid dupes.

    Returns:
        Deduplicated list of evidence dicts, each with:
            openalex_id, title, year, venue, venue_type, doi,
            citation_count, is_open_access, pmid, source ("openalex"),
            match_tier ("direct" | "company").
    """
    clean = _clean_name(device_name)
    company_short = _get_company_name(company)
    existing = existing_pmids or set()

    seen_ids: set[str] = set()  # openalex IDs for dedup across tiers
    results: list[dict] = []

    def _add(works: list[dict], tier: str) -> None:
        for w in works:
            oa_id = w["openalex_id"]
            if oa_id in seen_ids:
                continue
            # Deduplicate against existing PubMed PMIDs
            if w["pmid"] and w["pmid"] in existing:
                seen_ids.add(oa_id)
                continue
            w["match_tier"] = tier
            results.append(w)
            seen_ids.add(oa_id)

    # Tier 1: exact device name search
    if _is_searchable(clean):
        tier1 = _search_openalex(
            query="",
            filter_str=f"default.search:{clean}",
            max_results=50,
        )
        _add(tier1, "direct")
        time.sleep(PUBMED_DELAY)

    # Tier 2: company + device name (only if tier 1 found few results)
    if len(results) < 5 and company_short and len(company_short) > 3 and _is_searchable(clean):
        tier2 = _search_openalex(
            query=f"{company_short} {clean}",
            max_results=30,
        )
        _add(tier2, "direct")
        time.sleep(PUBMED_DELAY)

    # Tier 3: company + AI keywords (only if still empty)
    if len(results) == 0 and company_short and len(company_short) > 5:
        tier3 = _search_openalex(
            query=f"{company_short} artificial intelligence machine learning deep learning",
            max_results=15,
        )
        _add(tier3, "company")
        time.sleep(PUBMED_DELAY)

    # Post-filter: verify device name or company appears in title
    clean_norm = _normalize(clean)
    company_norm = _normalize(company_short)

    filtered: list[dict] = []
    for r in results:
        title_norm = _normalize(r["title"])
        if r["match_tier"] == "direct":
            # Must mention device name in title
            if clean_norm and len(clean_norm) > 3 and clean_norm in title_norm:
                filtered.append(r)
            # Also accept if DOI-linked and company name is in title
            elif company_norm and company_norm in title_norm:
                filtered.append(r)
        elif r["match_tier"] == "company":
            # Must mention company OR device in title, plus AI keyword
            has_entity = (
                (company_norm and company_norm in title_norm)
                or (clean_norm and len(clean_norm) > 3 and clean_norm in title_norm)
            )
            has_ai = any(kw in title_norm for kw in (
                "artificial intelligence", "machine learning", "deep learning",
                "algorithm", "automated", "computer aided", "computer-aided",
                "neural network", "convolutional",
            ))
            if has_entity and has_ai:
                filtered.append(r)

    return filtered


# ── CLI test harness ─────────────────────────────────────────────────


if __name__ == "__main__":
    test_cases = [
        ("Viz LVO", "Viz.ai, Inc."),
        ("IDx-DR", "Digital Diagnostics Inc."),
        ("Aidoc BriefCase", "Aidoc Medical, Ltd."),
    ]

    for name, company in test_cases:
        hits = enrich_device(name, company)
        direct = sum(1 for r in hits if r.get("match_tier") == "direct")
        indirect = sum(1 for r in hits if r.get("match_tier") == "company")
        print(f"\n=== {name} ({company}) ===")
        print(f"  {len(hits)} results ({direct} direct, {indirect} company-tier)")
        for r in hits[:5]:
            oa = "OA" if r["is_open_access"] else "closed"
            print(
                f"  [{r['match_tier']}] ({r['venue_type']}, {r['year']}, "
                f"cited:{r['citation_count']}, {oa}) {r['title'][:80]}"
            )

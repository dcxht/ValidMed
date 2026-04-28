"""Enrich devices with published evidence from PubMed.

Search strategy (multi-tier):
  1. Exact device name in title/abstract — high confidence
  2. Device name + company name together — medium confidence
  3. Company name + product category keywords — lower confidence, tagged as "indirect"
"""

import re
import time

import httpx

from config import NCBI_API_KEY, PUBMED_BASE, PUBMED_DELAY
from device_aliases import get_search_queries

SKIP_NAMES = {"ct", "mri", "ai", "x-ray", "ecg", "ekg", "ultrasound", "dose", "software"}

# Device names that are common English words or generic medical/technical terms.
# These MUST be searched with company affiliation, never alone.
GENERIC_NAMES = {
    "rapid", "dose", "clear", "smart", "insight", "air", "view", "pulse",
    "deep", "auto", "reveal", "impala", "precise", "prime", "elite",
    "vision", "clinical", "health", "care", "scan", "detect", "alert",
    "triage", "assist", "guide", "flow", "path", "link", "core", "life",
    "vital", "swift", "bright", "pro", "max", "plus", "ultra", "nova",
    "apex", "atlas", "echo", "aura", "wave", "beam", "star", "point",
    "image", "reconstruction", "segmentation", "detection", "learning",
    "diagnosis", "analysis", "processing", "enhancement", "contour",
    "fusion", "motion", "sync", "capture", "track", "monitor", "connect",
    "studio", "workspace", "platform", "suite", "system", "module",
}


def _is_generic_name(device_name: str) -> bool:
    """Check if a device name is too ambiguous to search alone.

    A name is generic if:
    - All words are common English/medical terms, OR
    - The name is very short (1-2 words), OR
    - The name contains only common technical terms
    """
    clean = _clean_name(device_name).lower()
    words = [w for w in re.findall(r'[a-z]+', clean) if len(w) > 1]

    if not words:
        return True
    # All words are generic
    if set(words).issubset(GENERIC_NAMES):
        return True
    # Name is only 1-2 meaningful words (high false positive risk)
    if len(words) <= 2 and any(w in GENERIC_NAMES for w in words):
        return True
    # Name is a single short word (even if not in our list)
    if len(words) == 1 and len(words[0]) <= 6:
        return True
    return False

# Map FDA specialty panels to PubMed search terms
SPECIALTY_TERMS = {
    "Radiology": "radiology OR imaging OR radiograph*",
    "Cardiovascular": "cardiology OR cardiac OR cardiovascular OR echocardiograph*",
    "Neurology": "neurology OR neurological OR brain OR stroke",
    "Gastroenterology-Urology": "gastroenterology OR endoscopy OR colonoscopy",
    "Ophthalmic": "ophthalmology OR retinal OR ophthalmic",
    "Pathology": "pathology OR histology OR cytology",
    "Hematology": "hematology OR blood",
    "Anesthesiology": "anesthesiology OR monitoring",
}


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
    # Remove trailing model numbers in parens like (DM5100)
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
    # Take everything before the first comma or common suffix
    name = company.split(",")[0].strip()
    # Remove common suffixes
    for suffix in (" Inc", " LLC", " Ltd", " Corp", " S.A.", " SAS", " BV",
                   " GmbH", " Co.", " Medical Systems", " Medical", " Health",
                   " Technologies", " Diagnostics"):
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    return name


def _search(query: str, max_results: int = 100) -> tuple[list[str], int]:
    """Execute a PubMed search with retries. Returns (pmid_list, total_count)."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    for attempt in range(3):
        try:
            resp = httpx.get(f"{PUBMED_BASE}/esearch.fcgi", params=params, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data = resp.json()
            result = data.get("esearchresult", {})
            pmids = result.get("idlist", [])
            total = int(result.get("count", len(pmids)))
            return pmids, total
        except Exception:
            time.sleep(2 ** attempt)

    return [], 0


def fetch_abstracts(pmids: list[str]) -> dict[str, str]:
    """Fetch abstracts for a list of PMIDs via efetch XML. Returns {pmid: abstract_text}."""
    if not pmids:
        return {}

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    for attempt in range(3):
        try:
            resp = httpx.get(f"{PUBMED_BASE}/efetch.fcgi", params=params, timeout=60)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            break
        except Exception:
            time.sleep(2 ** attempt)
    else:
        return {}

    # Parse XML to extract abstracts per PMID
    abstracts = {}
    text = resp.text
    # Split by article
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(text)
        for article in root.findall(".//PubmedArticle"):
            pmid_el = article.find(".//PMID")
            if pmid_el is None:
                continue
            pmid = pmid_el.text
            abstract_parts = article.findall(".//AbstractText")
            if abstract_parts:
                abstract = " ".join(part.text or "" for part in abstract_parts)
                abstracts[pmid] = abstract[:1000]  # Cap at 1000 chars
    except ET.ParseError:
        pass

    return abstracts


def fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    for attempt in range(3):
        try:
            resp = httpx.get(f"{PUBMED_BASE}/esummary.fcgi", params=params, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            break
        except Exception:
            time.sleep(2 ** attempt)
    else:
        return []

    data = resp.json()

    results = []
    for pmid in pmids:
        article = data.get("result", {}).get(pmid, {})
        if not article or "error" in article:
            continue

        results.append({
            "pmid": pmid,
            "title": article.get("title", ""),
            "journal": article.get("fulljournalname", article.get("source", "")),
            "pub_date": article.get("pubdate", ""),
            "study_type": _classify_study_type(article),
        })

    return results


def _classify_study_type(article: dict) -> str:
    """Classify study type using PubMed metadata + title keyword fallback.

    PubMed's pubtype field often misses RCTs and clinical trials for device
    studies. We supplement with title-based keyword detection.
    """
    pub_types = [pt.lower() for pt in article.get("pubtype", [])]
    title = article.get("title", "").lower()

    # Check PubMed metadata first
    if "randomized controlled trial" in pub_types:
        return "RCT"
    if "clinical trial" in pub_types or any("clinical trial" in pt for pt in pub_types):
        return "clinical_trial"
    if "meta-analysis" in pub_types:
        return "meta_analysis"
    if "systematic review" in pub_types:
        return "systematic_review"

    # Title-based fallback — catches device RCTs that PubMed doesn't tag
    if any(kw in title for kw in ("randomized", "randomised", "rct", "random assignment")):
        return "RCT"
    if any(kw in title for kw in ("clinical trial", "pivotal trial", "pivotal study",
                                   "prospective trial", "multicenter trial",
                                   "multicentre trial", "registration trial")):
        return "clinical_trial"
    if any(kw in title for kw in ("meta-analysis", "meta analysis", "metaanalysis")):
        return "meta_analysis"
    if any(kw in title for kw in ("systematic review", "systematicreview", "scoping review")):
        return "systematic_review"
    if any(kw in title for kw in ("prospective", "validation study", "clinical validation",
                                   "clinical evaluation", "clinical performance",
                                   "diagnostic accuracy", "real-world")):
        return "clinical_study"

    # PubMed metadata fallback for weaker types
    if "review" in pub_types:
        return "review"
    if "case reports" in pub_types:
        return "case_report"
    if "validation study" in pub_types or "comparative study" in pub_types:
        return "clinical_study"

    return "other"


def enrich_device(device_name: str, company: str, specialty: str = "") -> list[dict]:
    """Multi-tier PubMed search for a device.

    Returns deduplicated list of articles with a 'match_tier' field:
      - "direct": device name found in title/abstract
      - "company": company + device category search
    """
    clean = _clean_name(device_name)
    company_clean = _get_company_name(company)
    all_pmids = {}  # pmid -> tier

    total_pubmed_count = 0

    is_generic = _is_generic_name(device_name)

    # Tier 0 (alias expansion): search curated aliases as exact phrases only
    # Skip broad/free-text queries — only use properly quoted device names
    alias_queries = get_search_queries(device_name, company)
    for aq in alias_queries:
        # Only use queries that are a single quoted phrase like "Viz LVO"
        # Skip compound queries like '"Company" AI' or multi-term searches
        aq_stripped = aq.strip()
        if not (aq_stripped.startswith('"') and aq_stripped.endswith('"')):
            continue  # Skip non-phrase queries (too broad)

        if is_generic:
            if company_clean and len(company_clean) > 3:
                query = f'{aq_stripped}[tiab] AND "{company_clean}"[ad]'
            else:
                continue
        else:
            query = f'{aq_stripped}[tiab]'
        pmids_a, total_a = _search(query)
        if total_a > total_pubmed_count:
            total_pubmed_count = total_a
        time.sleep(PUBMED_DELAY)
        for p in pmids_a:
            if p not in all_pmids:
                all_pmids[p] = "direct"

    # Tier 1: Exact device name in title/abstract
    if _is_searchable(clean):
        if is_generic and company_clean and len(company_clean) > 3:
            # Generic name: MUST include company affiliation
            query1 = f'"{clean}"[tiab] AND "{company_clean}"[ad]'
        elif is_generic:
            query1 = None  # Can't search generic name without company
        else:
            query1 = f'"{clean}"[tiab]'

        if query1:
            pmids, total = _search(query1)
            total_pubmed_count = total
            time.sleep(PUBMED_DELAY)
            for p in pmids:
                all_pmids[p] = "direct"

    # Tier 2: Company name + device name
    if company_clean and len(company_clean) > 3:
        if len(all_pmids) < 5:
            query2 = f'"{company_clean}"[ad] AND "{clean}"[tiab]'
            if _is_searchable(clean):
                pmids2, _ = _search(query2)
                time.sleep(PUBMED_DELAY)
                for p in pmids2:
                    if p not in all_pmids:
                        all_pmids[p] = "direct"

    # Tier 3: Company in author affiliation + AI/ML keywords
    # Much stricter than before — searches [ad] (affiliation) not [tiab]
    # Only if we still have zero direct results
    if len(all_pmids) == 0 and company_clean and len(company_clean) > 5:
        # Company must be in author affiliation, not just mentioned in text
        query3 = f'"{company_clean}"[ad] AND ("artificial intelligence" OR "machine learning" OR "deep learning")[tiab]'
        pmids3, _ = _search(query3, max_results=10)
        time.sleep(PUBMED_DELAY)
        for p in pmids3:
            if p not in all_pmids:
                all_pmids[p] = "company"

    if not all_pmids:
        return []

    # Fetch details for all unique PMIDs
    details = fetch_pubmed_details(list(all_pmids.keys()))
    time.sleep(PUBMED_DELAY)

    # Tag each result with its match tier
    for article in details:
        article["match_tier"] = all_pmids.get(article["pmid"], "unknown")

    # Post-filter: for "direct" tier, PubMed already matched on tiab so we trust it.
    # For "company" tier, verify relevance — title should mention AI/ML/algorithm/device.
    filtered = []
    for article in details:
        if article["match_tier"] == "direct":
            filtered.append(article)
        elif article["match_tier"] == "company":
            title_lower = _normalize(article["title"])
            if any(kw in title_lower for kw in (
                "artificial intelligence", "machine learning", "deep learning",
                "algorithm", "automated", "computer-aided", "computer aided",
                "ai-", "ai ", "neural network", "convolutional",
                _normalize(clean) if len(clean) > 5 else "XNOMATCHX"
            )):
                filtered.append(article)

    return filtered


if __name__ == "__main__":
    test_cases = [
        ("Viz LVO", "Viz.ai, Inc.", "Neurology"),
        ("AIR Recon DL", "Ge Medical Systems, LLC", "Radiology"),
        ("SugarBug (1.x)", "Bench7, Inc.", "Dental"),
        ("IDx-DR", "Digital Diagnostics Inc.", "Ophthalmic"),
        ("Caption Guidance", "Caption Health, Inc.", "Cardiovascular"),
        ("Aidoc BriefCase", "Aidoc Medical, Ltd.", "Radiology"),
    ]

    for name, company, spec in test_cases:
        results = enrich_device(name, company, spec)
        direct = sum(1 for r in results if r.get("match_tier") == "direct")
        indirect = sum(1 for r in results if r.get("match_tier") == "company")
        print(f"\n=== {name} ({company}) ===")
        print(f"  {len(results)} articles ({direct} direct, {indirect} company-tier)")
        for r in results[:3]:
            print(f"  [{r['match_tier']}] {r['title'][:85]}")

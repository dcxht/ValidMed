"""Enrich De Novo (DEN) devices by downloading and parsing FDA decision summaries.

De Novo decision summaries are the richest regulatory documents for AI/ML devices
(20-75 pages of detailed clinical study results). About ~50 AI/ML devices came
through the De Novo pathway (~3.2% of 1,430 total).

Usage:
  python enrich_denovo.py                              # uses enriched_final_v2.json
  python enrich_denovo.py data/enriched_final_v2.json  # explicit path
"""

import json
import re
import sys
import time
from pathlib import Path

import fitz  # pymupdf
import httpx

DATA_DIR = Path(__file__).parent / "data"
PDF_DIR = DATA_DIR / "denovo_pdfs"

DENOVO_PDF_BASE = "https://www.accessdata.fda.gov/cdrh_docs/reviews"
DOWNLOAD_DELAY = 1.0  # be polite to FDA servers


# ---------------------------------------------------------------------------
# PDF download
# ---------------------------------------------------------------------------

def download_denovo_pdf(den_number: str) -> Path | None:
    """Download a De Novo decision summary PDF from FDA.

    Returns the local file path on success, None on 404 or failure.
    """
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    local_path = PDF_DIR / f"{den_number}.pdf"

    if local_path.exists() and local_path.stat().st_size > 0:
        return local_path

    url = f"{DENOVO_PDF_BASE}/{den_number}.pdf"

    for attempt in range(3):
        try:
            resp = httpx.get(url, timeout=60, follow_redirects=True)
            if resp.status_code == 404:
                print(f"  {den_number}: 404 not found", flush=True)
                return None
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()

            # Verify we actually got a PDF (FDA sometimes returns HTML error pages)
            if not resp.content[:5].startswith(b"%PDF"):
                print(f"  {den_number}: response is not a PDF", flush=True)
                return None

            local_path.write_bytes(resp.content)
            print(f"  {den_number}: downloaded ({len(resp.content) // 1024} KB)", flush=True)
            return local_path

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"  {den_number}: download failed — {e}", flush=True)
                return None

    return None


# ---------------------------------------------------------------------------
# Text extraction from PDF
# ---------------------------------------------------------------------------

def _extract_text(pdf_path: Path) -> str:
    """Extract full text from a PDF using pymupdf."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def _extract_first_pages(pdf_path: Path, n: int = 3) -> str:
    """Extract text from the first N pages (for indications_for_use etc.)."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        if i >= n:
            break
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


# ---------------------------------------------------------------------------
# Regex-based clinical data extraction
# ---------------------------------------------------------------------------

_PCT_PATTERN = r"(\d{1,3}(?:\.\d+)?)\s*%"
_NUM_PATTERN = r"(\d[\d,]*)"

# Sensitivity / specificity / AUC
_SENSITIVITY_RE = re.compile(
    r"sensitivit[yies]+\s*(?:of|was|=|:)?\s*" + _PCT_PATTERN, re.IGNORECASE
)
_SPECIFICITY_RE = re.compile(
    r"specificit[yies]+\s*(?:of|was|=|:)?\s*" + _PCT_PATTERN, re.IGNORECASE
)
_AUC_RE = re.compile(
    r"(?:AUC|AUROC|area\s+under\s+(?:the\s+)?(?:ROC\s+)?curve)\s*"
    r"(?:of|was|=|:)?\s*(0?\.\d+|\d\.\d+)",
    re.IGNORECASE,
)

# Sample size
_SAMPLE_SIZE_RE = re.compile(
    r"(?:sample\s+size|(?:total\s+of|included|enrolled|comprising|consisted\s+of))\s*"
    r"(?:of\s+|was\s+)?" + _NUM_PATTERN + r"\s*(?:subjects?|patients?|cases?|images?|samples?|studies|exams?)",
    re.IGNORECASE,
)

# Number of clinical sites
_SITES_RE = re.compile(
    r"(\d{1,3})\s*(?:clinical\s+)?sites?", re.IGNORECASE
)

# Study design
_PROSPECTIVE_RE = re.compile(r"\bprospective\b", re.IGNORECASE)
_RETROSPECTIVE_RE = re.compile(r"\bretrospective\b", re.IGNORECASE)

# Primary endpoint
_ENDPOINT_RE = re.compile(
    r"(?:primary\s+endpoint|primary\s+performance\s+(?:goal|endpoint|criterion))"
    r"\s*(?:was|is|:)?\s*(.{10,200}?)(?:\.|$)",
    re.IGNORECASE,
)

# Ground truth
_GROUND_TRUTH_RE = re.compile(
    r"(?:ground\s+truth|reference\s+standard|gold\s+standard|truth\s+(?:standard|label))"
    r"\s*(?:was|is|:)?\s*(.{10,200}?)(?:\.|$)",
    re.IGNORECASE,
)

# Special controls
_SPECIAL_CONTROLS_RE = re.compile(
    r"(?:special\s+controls?)\s*(?:include|are|:)?\s*(.{10,500}?)(?:\n\n|$)",
    re.IGNORECASE,
)

# Indications for use
_INDICATIONS_RE = re.compile(
    r"(?:indications?\s+for\s+use|intended\s+use)\s*(?::)?\s*(.{20,1000}?)(?:\n\n|Contraindications?|Warnings?|Device\s+Description)",
    re.IGNORECASE | re.DOTALL,
)


def _first_match(pattern: re.Pattern, text: str) -> str | None:
    """Return first capture group from pattern match, or None."""
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _first_float(pattern: re.Pattern, text: str) -> float | None:
    """Return first match as float, or None."""
    m = pattern.search(text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def _first_int(pattern: re.Pattern, text: str) -> int | None:
    """Return first match as int, or None."""
    m = pattern.search(text)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def _extract_clinical_section(full_text: str) -> str:
    """Extract the clinical study section from a decision summary."""
    # Look for common section headings
    patterns = [
        r"(?:^|\n)\s*(?:VI+\.?\s*)?Clinical\s+(?:Studies?|Performance|Evidence|Data)",
        r"(?:^|\n)\s*Clinical\s+Study\s+Summary",
        r"(?:^|\n)\s*(?:Summary\s+of\s+)?Clinical\s+(?:Testing|Validation|Study)",
    ]
    start = None
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            start = m.start()
            break

    if start is None:
        return full_text  # fall back to full text

    # Try to find the next major section heading after clinical
    end_patterns = [
        r"(?:^|\n)\s*(?:VI+\.?\s*)?(?:Benefit|Risk|Labeling|Manufacturing|Conclusion|Summary|Appendix)",
    ]
    clinical_text = full_text[start:]
    for pat in end_patterns:
        m = re.search(pat, clinical_text[200:], re.IGNORECASE)  # skip first 200 chars
        if m:
            clinical_text = clinical_text[: m.start() + 200]
            break

    return clinical_text


def _determine_study_design(text: str) -> str | None:
    """Determine if the clinical study was prospective, retrospective, or both."""
    has_prospective = bool(_PROSPECTIVE_RE.search(text))
    has_retrospective = bool(_RETROSPECTIVE_RE.search(text))

    if has_prospective and has_retrospective:
        return "prospective_and_retrospective"
    elif has_prospective:
        return "prospective"
    elif has_retrospective:
        return "retrospective"
    return None


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_denovo_summary(den_number: str) -> dict:
    """Download (if needed) and parse a De Novo decision summary PDF.

    Returns a dict with extracted clinical data fields.
    Missing fields are set to None.
    """
    result = {
        "den_number": den_number,
        "pdf_url": f"{DENOVO_PDF_BASE}/{den_number}.pdf",
        "pdf_downloaded": False,
        "indications_for_use": None,
        "clinical_study_summary": None,
        "sensitivity": None,
        "specificity": None,
        "auc": None,
        "sample_size": None,
        "number_of_sites": None,
        "study_design": None,
        "primary_endpoint": None,
        "ground_truth": None,
        "special_controls": None,
    }

    pdf_path = download_denovo_pdf(den_number)
    if pdf_path is None:
        return result

    result["pdf_downloaded"] = True

    # Extract text
    full_text = _extract_text(pdf_path)
    front_text = _extract_first_pages(pdf_path, n=3)
    clinical_text = _extract_clinical_section(full_text)

    # Indications for use — usually in first few pages
    result["indications_for_use"] = _first_match(_INDICATIONS_RE, front_text)
    if result["indications_for_use"] is None:
        # Try full text as fallback
        result["indications_for_use"] = _first_match(_INDICATIONS_RE, full_text)

    # Clinical study summary — first 500 chars of the clinical section
    if clinical_text != full_text:
        # We found a distinct clinical section
        summary_text = clinical_text[:2000].strip()
        # Clean up whitespace
        summary_text = re.sub(r"\s+", " ", summary_text)
        result["clinical_study_summary"] = summary_text[:500]

    # Performance metrics — search clinical section first, then full text
    for text_source in [clinical_text, full_text]:
        if result["sensitivity"] is None:
            result["sensitivity"] = _first_float(_SENSITIVITY_RE, text_source)
        if result["specificity"] is None:
            result["specificity"] = _first_float(_SPECIFICITY_RE, text_source)
        if result["auc"] is None:
            result["auc"] = _first_float(_AUC_RE, text_source)
        if result["sample_size"] is None:
            result["sample_size"] = _first_int(_SAMPLE_SIZE_RE, text_source)
        if result["number_of_sites"] is None:
            result["number_of_sites"] = _first_int(_SITES_RE, text_source)
        if result["primary_endpoint"] is None:
            result["primary_endpoint"] = _first_match(_ENDPOINT_RE, text_source)
        if result["ground_truth"] is None:
            result["ground_truth"] = _first_match(_GROUND_TRUTH_RE, text_source)

    # Study design — from clinical section
    result["study_design"] = _determine_study_design(clinical_text)

    # Special controls — often in a dedicated section, search full text
    result["special_controls"] = _first_match(_SPECIAL_CONTROLS_RE, full_text)

    return result


# ---------------------------------------------------------------------------
# Batch enrichment
# ---------------------------------------------------------------------------

def enrich_denovo_devices(devices: list[dict]) -> list[dict]:
    """Enrich only De Novo (DEN) devices with parsed decision summary data.

    Skips devices whose fda_submission_number does not start with 'DEN'.
    Adds a 'denovo_summary' key to each processed device.
    """
    den_devices = [
        (i, d) for i, d in enumerate(devices)
        if d.get("fda_submission_number", "").upper().startswith("DEN")
    ]

    if not den_devices:
        print("No De Novo devices found in dataset.", flush=True)
        return devices

    print(f"Found {len(den_devices)} De Novo devices to enrich.", flush=True)

    for idx, (i, device) in enumerate(den_devices):
        den_number = device["fda_submission_number"].strip().upper()
        print(f"\n[{idx + 1}/{len(den_devices)}] {den_number} — {device.get('device_name', 'unknown')}")

        summary = parse_denovo_summary(den_number)
        device["denovo_summary"] = summary

        # Surface key metrics at top level for easy access
        if summary.get("sensitivity") is not None:
            device.setdefault("sensitivity", summary["sensitivity"])
        if summary.get("specificity") is not None:
            device.setdefault("specificity", summary["specificity"])
        if summary.get("auc") is not None:
            device.setdefault("auc", summary["auc"])
        if summary.get("indications_for_use") is not None:
            device.setdefault("indications_for_use", summary["indications_for_use"])

        time.sleep(DOWNLOAD_DELAY)

    # Print summary
    downloaded = sum(
        1 for _, d in den_devices if d.get("denovo_summary", {}).get("pdf_downloaded")
    )
    has_sensitivity = sum(
        1 for _, d in den_devices if d.get("denovo_summary", {}).get("sensitivity") is not None
    )
    has_auc = sum(
        1 for _, d in den_devices if d.get("denovo_summary", {}).get("auc") is not None
    )

    print(f"\n{'=' * 60}")
    print(f"De Novo Enrichment Summary")
    print(f"{'=' * 60}")
    print(f"Total De Novo devices:     {len(den_devices)}")
    print(f"PDFs downloaded:           {downloaded}")
    print(f"With sensitivity:          {has_sensitivity}")
    print(f"With AUC:                  {has_auc}")
    print(f"{'=' * 60}")

    return devices


# ---------------------------------------------------------------------------
# Standalone mode
# ---------------------------------------------------------------------------

def _find_enriched_json() -> Path:
    """Find the most recent enriched JSON in the data directory."""
    candidates = [
        DATA_DIR / "enriched_final_v2.json",
        DATA_DIR / "enriched_final.json",
        DATA_DIR / "enriched_pass2_full.json",
    ]
    # Also check checkpoints in descending order
    for cp in sorted(DATA_DIR.glob("enriched_checkpoint_*.json"), reverse=True):
        candidates.append(cp)

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(f"No enriched JSON found in {DATA_DIR}")


def main():
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        input_path = _find_enriched_json()

    print(f"Loading devices from {input_path}")
    with open(input_path) as f:
        devices = json.load(f)
    print(f"Loaded {len(devices)} devices.")

    devices = enrich_denovo_devices(devices)

    out_path = DATA_DIR / "enriched_denovo.json"
    with open(out_path, "w") as f:
        json.dump(devices, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()

"""
enrich_510k_summaries.py
Download and parse FDA 510(k) summary PDFs to extract clinical performance data.

URL pattern: https://www.accessdata.fda.gov/cdrh_docs/pdf{YY}/{K_NUMBER}.pdf
Uses PyMuPDF (fitz) for text extraction and regex for metric parsing.
"""

import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
import httpx

from config import OPENFDA_DELAY  # reuse project rate-limit convention

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FDA_PDF_BASE = "https://www.accessdata.fda.gov/cdrh_docs"
PDF_DIR = Path(__file__).resolve().parent / "data" / "510k_pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

FDA_DELAY = 1.0  # 1 request per second for FDA downloads


# ---------------------------------------------------------------------------
# 1. Download
# ---------------------------------------------------------------------------

def _k_number_to_url(k_number: str) -> str:
    """Build the FDA PDF URL from a K number like K213456."""
    k = k_number.strip().upper()
    # Extract 2-digit year: K213456 -> '21'
    yy = k[1:3]
    return f"{FDA_PDF_BASE}/pdf{yy}/{k}.pdf"


def download_pdf(k_number: str) -> Path | None:
    """Download a 510(k) summary PDF. Returns local path or None on failure."""
    k = k_number.strip().upper()
    local_path = PDF_DIR / f"{k}.pdf"

    if local_path.exists():
        log.debug("PDF already cached: %s", local_path)
        return local_path

    url = _k_number_to_url(k)
    log.info("Downloading %s", url)

    try:
        resp = httpx.get(url, timeout=30, headers={"User-Agent": "ValidMed/1.0"})
        if resp.status_code == 404:
            log.warning("PDF not found (404): %s", url)
            return None
        resp.raise_for_status()
    except httpx.RequestError as exc:
        log.error("Download failed for %s: %s", k, exc)
        return None

    # Sanity check: real PDFs start with %PDF
    if not resp.content[:5].startswith(b"%PDF"):
        log.warning("Response for %s is not a PDF (bad magic bytes)", k)
        return None

    local_path.write_bytes(resp.content)
    log.info("Saved %s (%d bytes)", local_path.name, len(resp.content))
    return local_path


# ---------------------------------------------------------------------------
# 2. Extract text
# ---------------------------------------------------------------------------

def extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    text_parts: list[str] = []
    try:
        with fitz.open(str(pdf_path)) as doc:
            for page in doc:
                text_parts.append(page.get_text())
    except Exception as exc:
        log.error("Text extraction failed for %s: %s", pdf_path, exc)
        return ""
    return "\n".join(text_parts)


# ---------------------------------------------------------------------------
# 3. Regex-based clinical performance parsing
# ---------------------------------------------------------------------------

def _find_percentage(text: str, patterns: list[str]) -> str | None:
    """Search text for any of the given keyword patterns followed by a percentage."""
    for pat in patterns:
        # Match: keyword ... number% or keyword ... 0.XXX
        match = re.search(
            rf"{pat}\s*[:=]?\s*(\d{{1,3}}(?:\.\d+)?)\s*%",
            text, re.IGNORECASE,
        )
        if match:
            return f"{match.group(1)}%"
        # Decimal form (e.g., 0.95)
        match = re.search(
            rf"{pat}\s*[:=]?\s*(0\.\d+)",
            text, re.IGNORECASE,
        )
        if match:
            return match.group(1)
    return None


def _find_sample_size(text: str) -> int | None:
    """Look for sample size indicators and return the largest plausible number."""
    patterns = [
        r"(?:N\s*=\s*)(\d[\d,]*)",
        r"(\d[\d,]*)\s*(?:patients|subjects|cases|images|studies|exams|readers)",
        r"(?:total\s+of\s+)(\d[\d,]*)",
        r"(?:sample\s+size\s*[:=]?\s*)(\d[\d,]*)",
    ]
    candidates: list[int] = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            raw = m.group(1).replace(",", "")
            try:
                n = int(raw)
                if 5 <= n <= 10_000_000:  # plausible range
                    candidates.append(n)
            except ValueError:
                continue
    return max(candidates) if candidates else None


def _find_study_design(text: str) -> list[str]:
    """Identify study design keywords present in the text."""
    keywords = {
        "retrospective": r"retrospective",
        "prospective": r"prospective",
        "multi-site": r"multi[- ]?(?:site|center|centre)",
        "single-site": r"single[- ]?(?:site|center|centre)",
        "randomized": r"randomi[sz]ed",
        "blinded": r"(?:double|single)[- ]?blind",
    }
    found = []
    for label, pat in keywords.items():
        if re.search(pat, text, re.IGNORECASE):
            found.append(label)
    return found


def _find_ground_truth(text: str) -> str | None:
    """Look for ground truth / reference standard description."""
    patterns = [
        r"(?:ground\s+truth|reference\s+standard|gold\s+standard)\s*[:=]?\s*([^\n.]{5,80})",
        r"(?:ground\s+truth|reference\s+standard|gold\s+standard)\s+(?:was|were|is)\s+([^\n.]{5,80})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    # Just flag presence
    if re.search(r"ground\s+truth|reference\s+standard|gold\s+standard", text, re.IGNORECASE):
        return "mentioned (could not extract details)"
    return None


def parse_clinical_data(text: str) -> dict:
    """Parse clinical performance metrics from extracted PDF text."""
    sensitivity = _find_percentage(text, [
        r"sensitivity", r"sens\b", r"true\s+positive\s+rate", r"TPR",
    ])
    specificity = _find_percentage(text, [
        r"specificity", r"spec\b", r"true\s+negative\s+rate", r"TNR",
    ])
    auc = _find_percentage(text, [
        r"AUROC", r"AUC", r"area\s+under\s+(?:the\s+)?(?:ROC\s+)?curve",
        r"area\s+under",
    ])
    sample_size = _find_sample_size(text)
    study_design = _find_study_design(text)
    ground_truth = _find_ground_truth(text)

    has_clinical_data = any([sensitivity, specificity, auc, sample_size, study_design])

    return {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "auc": auc,
        "sample_size": sample_size,
        "study_design": study_design if study_design else None,
        "ground_truth": ground_truth,
        "has_clinical_data": has_clinical_data,
    }


# ---------------------------------------------------------------------------
# 4. Main entry point
# ---------------------------------------------------------------------------

def parse_510k_summary(k_number: str) -> dict | None:
    """
    Download and parse a single 510(k) summary PDF.
    Returns a dict of extracted clinical data, or None if PDF not available.
    """
    pdf_path = download_pdf(k_number)
    if pdf_path is None:
        return None

    text = extract_text(pdf_path)
    if not text.strip():
        log.warning("No text extracted from %s", k_number)
        return {"has_clinical_data": False, "error": "no_text_extracted"}

    result = parse_clinical_data(text)
    result["k_number"] = k_number.strip().upper()
    result["pdf_pages"] = len(fitz.open(str(pdf_path)))
    result["text_length"] = len(text)
    return result


# ---------------------------------------------------------------------------
# 5. Batch processing
# ---------------------------------------------------------------------------

def enrich_batch(devices: list[dict]) -> list[dict]:
    """
    Process a list of device dicts, adding a `regulatory_evidence` field to each.
    Expects each device dict to have a 'k_number' (or 'knumber' / '510k_number') key.
    """
    total = len(devices)
    for i, device in enumerate(devices):
        # Find the K number from common field names
        k_number = (
            device.get("k_number")
            or device.get("knumber")
            or device.get("510k_number")
            or device.get("kNumber")
            or ""
        )
        if not k_number:
            log.warning("Device %d/%d: no K number found, skipping", i + 1, total)
            device["regulatory_evidence"] = None
            continue

        log.info("Processing %d/%d: %s", i + 1, total, k_number)
        evidence = parse_510k_summary(k_number)
        device["regulatory_evidence"] = evidence

        # Rate limit
        if i < total - 1:
            time.sleep(FDA_DELAY)

    return devices


# ---------------------------------------------------------------------------
# 6. Standalone mode
# ---------------------------------------------------------------------------

def main():
    """CLI: pass a JSON file path of enriched devices, outputs enriched results."""
    if len(sys.argv) < 2:
        print("Usage: python enrich_510k_summaries.py <input.json> [output.json]")
        print("       python enrich_510k_summaries.py <K_NUMBER>")
        sys.exit(1)

    arg = sys.argv[1]

    # Single K number mode
    if arg.upper().startswith("K") and not arg.endswith(".json"):
        result = parse_510k_summary(arg)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"No PDF found for {arg}")
            sys.exit(1)
        return

    # Batch mode: JSON file
    input_path = Path(arg)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r") as f:
        devices = json.load(f)

    if not isinstance(devices, list):
        print("Expected a JSON array of device objects")
        sys.exit(1)

    log.info("Loaded %d devices from %s", len(devices), input_path)
    enriched = enrich_batch(devices)

    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".enriched.json")
    with open(output_path, "w") as f:
        json.dump(enriched, f, indent=2)

    # Summary stats
    with_data = sum(1 for d in enriched if d.get("regulatory_evidence", {}) and d["regulatory_evidence"].get("has_clinical_data"))
    log.info("Done. %d/%d devices have clinical performance data", with_data, len(enriched))
    log.info("Output saved to %s", output_path)


if __name__ == "__main__":
    main()

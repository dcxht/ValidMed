"""Extract clinical claims and evidence tiers from 510(k) summary PDFs using Claude Haiku.

For each device, extracts:
  - Intended use statement
  - Claim category (enhancement -> treatment planning)
  - Validation study design tier
  - Performance metrics (sensitivity, specificity, AUC)
  - Sample size, ground truth, limitations

Usage:
    python extract_claims.py                    # Process all PDFs
    python extract_claims.py --test 20          # Test on 20 PDFs
    python extract_claims.py --resume           # Resume from checkpoint
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
PDF_DIR = DATA_DIR / "510k_pdfs"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

EXTRACTION_PROMPT = """You are extracting clinical claims and validation evidence from an FDA 510(k) summary document for an AI/ML medical device.

Device: {device_name}
Company: {company}
FDA Submission: {k_number}
Specialty: {specialty}

Document text (from 510(k) summary PDF):
{pdf_text}

Extract the following as JSON. If a field is not mentioned in the document, set it to null.

{{
  "intended_use": "verbatim intended use or indications for use statement, as close to the original text as possible",
  "claim_category": "enhancement|quantification|detection|triage|diagnosis|treatment",
  "claim_category_rationale": "one sentence explaining why you chose this category",
  "claim_description": "brief plain-language description of what the device claims to do clinically",
  "autonomous_or_assistive": "autonomous|assistive|unclear",
  "target_condition": "the medical condition or clinical scenario the device addresses, or null",
  "target_population": "intended patient population (age, setting, etc.) or null",
  "validation_design": "none|bench_only|retrospective_single|retrospective_multi|prospective_single|prospective_multi|rct",
  "validation_design_rationale": "one sentence explaining the study design classification",
  "sensitivity": "reported value as string (e.g. '95.2%') or null",
  "specificity": "reported value as string or null",
  "auc": "reported value as string or null",
  "ppv": "reported value as string or null",
  "npv": "reported value as string or null",
  "accuracy": "reported value as string or null",
  "other_metrics": "any other reported performance metrics as a string, or null",
  "sample_size": integer or null,
  "num_sites": integer or null,
  "ground_truth": "reference standard or ground truth method used, or null",
  "comparator": "what the device was compared against (e.g. predicate device, expert readers), or null",
  "demographic_reporting": "yes|partial|no - did the summary report patient demographics?",
  "limitations_stated": "any limitations mentioned in the summary, or null"
}}

IMPORTANT CLASSIFICATION RULES:

CLAIM CATEGORIES (choose the HIGHEST applicable level):
  enhancement = image reconstruction, noise reduction, image quality improvement, denoising
  quantification = automated measurements, volumetric analysis, scoring, segmentation for measurement
  detection = flagging findings, identifying abnormalities, screening, computer-aided detection (CADe)
  triage = prioritizing worklists, routing urgent cases, notification, alerting clinicians (CADt)
  diagnosis = classifying conditions, providing differential, autonomous diagnostic assessment (CADx)
  treatment = ONLY if the device directly computes treatment parameters (radiation dose, surgical path). Do NOT classify as treatment just because the intended use says "assist in treatment planning" or "support clinical decisions" -- that language is standard FDA boilerplate for assistive devices.

VALIDATION DESIGN RULES (this is critical -- read carefully):
  none = the document contains NO description of any testing, validation, or performance evaluation
  bench_only = algorithm tested on a dataset of images/cases, even if from multiple institutions. If data was "collected from" or "sourced from" multiple sites but the algorithm was tested offline (not in a clinical workflow), this is bench_only, NOT retrospective_multi.
  retrospective_single = clinical study using retrospective patient data from ONE institution/site
  retrospective_multi = clinical study using retrospective patient data from MULTIPLE institutions, where the study was designed as a multi-site clinical study (not just data sourced from multiple databases)
  prospective_single = study where the device was tested on patients prospectively at ONE site
  prospective_multi = prospective study across MULTIPLE clinical sites
  rct = randomized controlled trial

KEY DISTINCTION: "Images were collected from 3 institutions" is bench_only (multi-source data).
"A multi-site clinical study was conducted at 3 hospitals" is retrospective_multi or prospective_multi.

- Extract performance metrics exactly as reported (include % signs, decimal points)
- Return ONLY valid JSON, no other text"""


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception:
        return ""


def _extract_performance_section(pdf_text: str) -> str:
    """Extract the section of the PDF most likely to contain performance data.

    510(k) summaries typically have performance data in sections titled
    'Performance Testing', 'Clinical Performance', 'Validation', 'Results',
    or near keywords like 'sensitivity', 'specificity', 'AUC'.
    """
    import re
    lower = pdf_text.lower()

    # Find the best starting point for performance data
    markers = [
        'performance testing', 'clinical performance', 'performance study',
        'validation testing', 'clinical study', 'clinical data',
        'standalone performance', 'clinical evaluation',
        'substantial equivalence', 'results',
    ]

    best_start = None
    for marker in markers:
        idx = lower.find(marker)
        if idx > 0 and (best_start is None or idx < best_start):
            best_start = idx

    # Also find where specific metrics appear
    for pattern in [r'sensitiv', r'specificit', r'auroc', r'auc\s*[=:]', r'accuracy\s*[=:]']:
        match = re.search(pattern, lower)
        if match:
            # Go back a bit to capture context
            metric_start = max(0, match.start() - 500)
            if best_start is None or metric_start < best_start:
                best_start = metric_start

    if best_start is not None:
        return pdf_text[best_start:best_start + 8000]

    return ""


def _regex_extract_metrics(pdf_text: str) -> dict:
    """Backstop: extract performance metrics via regex for anything the LLM misses."""
    import re
    metrics = {}

    patterns = {
        'sensitivity': r'[Ss]ensitivity\s*[=:]\s*([\d.]+\s*%?(?:\s*\(.*?\))?)',
        'specificity': r'[Ss]pecificity\s*[=:]\s*([\d.]+\s*%?(?:\s*\(.*?\))?)',
        'auc': r'(?:AUC|AUROC)\s*[=:]\s*([\d.]+(?:\s*\(.*?\))?)',
        'accuracy': r'[Aa]ccuracy\s*[=:]\s*([\d.]+\s*%?)',
        'sample_size': r'[Nn]\s*=\s*(\d{2,6})',
    }

    for name, pattern in patterns.items():
        match = re.search(pattern, pdf_text)
        if match:
            metrics[name] = match.group(1) if match.group(1) else match.group(0)

    # Sample size: find the largest plausible number near "patient/subject/case"
    if 'sample_size' not in metrics:
        sizes = re.findall(r'(\d{2,6})\s+(?:patients?|subjects?|cases?|images?|studies|exams?)', pdf_text)
        if sizes:
            metrics['sample_size'] = max(int(s) for s in sizes)

    return metrics


def extract_claims_llm(device_name: str, company: str, k_number: str,
                        specialty: str, pdf_text: str) -> dict | None:
    """Send PDF text to Claude Haiku for structured claim extraction."""
    if not ANTHROPIC_API_KEY:
        return None

    # Send as much text as possible. Haiku handles ~200K tokens.
    # Most 510(k) summaries are 10-30K chars (well within limits).
    truncated = pdf_text[:40000]

    prompt = EXTRACTION_PROMPT.format(
        device_name=device_name,
        company=company,
        k_number=k_number,
        specialty=specialty,
        pdf_text=truncated,
    )

    for attempt in range(3):
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
                timeout=60,
            )

            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue

            resp.raise_for_status()
            content = resp.json()["content"][0]["text"]

            # Parse JSON from response
            # Handle case where LLM wraps in ```json
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]

            result = json.loads(content)
            result["k_number"] = k_number
            result["extraction_source"] = "510k_pdf"

            # Backstop: fill in any metrics the LLM missed using regex
            regex_metrics = _regex_extract_metrics(pdf_text)
            for field in ['sensitivity', 'specificity', 'auc', 'accuracy', 'sample_size']:
                if not result.get(field) and regex_metrics.get(field):
                    result[field] = regex_metrics[field]
                    result.setdefault("_regex_backfill", []).append(field)

            return result

        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                    result["k_number"] = k_number
                    result["extraction_source"] = "510k_pdf"

                    # Same regex backstop
                    regex_metrics = _regex_extract_metrics(pdf_text)
                    for field in ['sensitivity', 'specificity', 'auc', 'accuracy', 'sample_size']:
                        if not result.get(field) and regex_metrics.get(field):
                            result[field] = regex_metrics[field]
                            result.setdefault("_regex_backfill", []).append(field)

                    return result
                except json.JSONDecodeError:
                    pass
            if attempt < 2:
                time.sleep(1)
                continue
            return None

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"    Error: {e}", flush=True)
            return None

    return None


def run_extraction(test_limit: int | None = None, resume: bool = False):
    """Extract claims from all 510(k) PDFs."""

    # Load device data
    enriched_path = DATA_DIR / "enriched_final.json"
    if not enriched_path.exists():
        print("No enriched_final.json found")
        sys.exit(1)

    with open(enriched_path) as f:
        devices = json.load(f)

    # Load checkpoint if resuming
    claims_path = DATA_DIR / "claims.json"
    existing_claims = {}
    if resume and claims_path.exists():
        with open(claims_path) as f:
            existing = json.load(f)
        existing_claims = {c["k_number"]: c for c in existing if c.get("k_number")}
        print(f"Resuming: {len(existing_claims)} already extracted", flush=True)

    total = len(devices)
    if test_limit:
        total = min(total, test_limit)

    claims = list(existing_claims.values())
    extracted = 0
    skipped = 0
    no_pdf = 0

    print(f"Extracting claims from {total} devices...", flush=True)

    for i, device in enumerate(devices[:total]):
        k_number = device.get("fda_submission_number", "")

        # Skip if already extracted
        if k_number in existing_claims:
            skipped += 1
            continue

        # Find PDF
        pdf_path = PDF_DIR / f"{k_number}.pdf"
        if not pdf_path.exists():
            no_pdf += 1
            continue

        # Extract text
        text = extract_text_from_pdf(str(pdf_path))
        if len(text) < 100:
            no_pdf += 1
            continue

        name = device.get("device_name", "")
        company = device.get("company", "")
        specialty = device.get("specialty_panel", "")

        if (i + 1) % 50 == 0 or i == 0:
            print(f"  [{i+1}/{total}] {name[:40]} (extracted={extracted}, no_pdf={no_pdf})", flush=True)

        result = extract_claims_llm(name, company, k_number, specialty, text)

        if result:
            result["device_name"] = name
            result["company"] = company
            result["specialty_panel"] = specialty
            claims.append(result)
            extracted += 1

        # Save checkpoint every 100
        if (extracted + 1) % 100 == 0:
            with open(claims_path, "w") as f:
                json.dump(claims, f, indent=2, default=str)

        time.sleep(0.3)  # Rate limit

    # Final save
    with open(claims_path, "w") as f:
        json.dump(claims, f, indent=2, default=str)

    print(f"\nDone:", flush=True)
    print(f"  Total devices: {total}", flush=True)
    print(f"  Claims extracted: {extracted}", flush=True)
    print(f"  Already had: {skipped}", flush=True)
    print(f"  No PDF available: {no_pdf}", flush=True)
    print(f"  Saved to {claims_path}", flush=True)

    # Print claim category distribution
    from collections import Counter
    categories = Counter(c.get("claim_category") for c in claims if c.get("claim_category"))
    designs = Counter(c.get("validation_design") for c in claims if c.get("validation_design"))

    print(f"\nClaim categories:", flush=True)
    for cat, n in categories.most_common():
        print(f"  {cat}: {n}", flush=True)

    print(f"\nValidation designs:", flush=True)
    for design, n in designs.most_common():
        print(f"  {design}: {n}", flush=True)


if __name__ == "__main__":
    test_limit = None
    resume = "--resume" in sys.argv

    for i, arg in enumerate(sys.argv):
        if arg == "--test" and i + 1 < len(sys.argv):
            test_limit = int(sys.argv[i + 1])

    run_extraction(test_limit=test_limit, resume=resume)

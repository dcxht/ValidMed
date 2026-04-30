"""Generate a stratified random sample of 150 devices for human validation.

Creates a CSV where each row has the LLM extraction alongside the PDF path,
so the reviewer can open the PDF and verify each field.

Usage:
    python generate_validation_sample.py
    # Then open data/validation_sample.csv and fill in human_* columns
    # Then run: python generate_validation_sample.py --compute
"""

import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PDF_DIR = DATA_DIR / "510k_pdfs"

CLAIM_TIERS = ["enhancement", "quantification", "detection", "triage", "diagnosis", "treatment"]
EVIDENCE_TIERS = ["none", "bench_only", "retrospective_single", "retrospective_multi",
                  "prospective_single", "prospective_multi", "rct"]


def generate_sample(n: int = 150):
    with open(DATA_DIR / "claims.json") as f:
        claims = json.load(f)

    # Only include devices with PDFs available
    valid = [c for c in claims if (PDF_DIR / f"{c.get('k_number', '')}.pdf").exists()]
    print(f"Devices with PDFs: {len(valid)}")

    # Stratified sample: proportional to claim_category distribution
    random.seed(42)
    by_category = {}
    for c in valid:
        cat = (c.get("claim_category") or "unknown").lower()
        by_category.setdefault(cat, []).append(c)

    sample = []
    for cat in CLAIM_TIERS:
        devices = by_category.get(cat, [])
        # Proportional allocation, minimum 10 per category
        allocation = max(10, round(len(devices) / len(valid) * n))
        allocation = min(allocation, len(devices))
        sample.extend(random.sample(devices, allocation))

    # Trim to exactly n if over
    if len(sample) > n:
        sample = random.sample(sample, n)

    # Write CSV
    out_path = DATA_DIR / "validation_sample.csv"
    fieldnames = [
        "k_number", "device_name", "company", "specialty_panel",
        "llm_claim_category", "llm_validation_design",
        "llm_sensitivity", "llm_specificity", "llm_auc",
        "llm_sample_size", "llm_intended_use",
        "pdf_path",
        "human_claim_category", "human_validation_design",
        "human_sensitivity_correct", "human_notes",
    ]

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in sample:
            k = c.get("k_number", "")
            writer.writerow({
                "k_number": k,
                "device_name": c.get("device_name", ""),
                "company": c.get("company", ""),
                "specialty_panel": c.get("specialty_panel", ""),
                "llm_claim_category": c.get("claim_category", ""),
                "llm_validation_design": c.get("validation_design", ""),
                "llm_sensitivity": c.get("sensitivity", ""),
                "llm_specificity": c.get("specificity", ""),
                "llm_auc": c.get("auc", ""),
                "llm_sample_size": c.get("sample_size", ""),
                "llm_intended_use": str(c.get("intended_use", ""))[:200],
                "pdf_path": str(PDF_DIR / f"{k}.pdf"),
                "human_claim_category": "",
                "human_validation_design": "",
                "human_sensitivity_correct": "",
                "human_notes": "",
            })

    # Print distribution
    print(f"\nGenerated {len(sample)} samples at {out_path}")
    cats = Counter(c.get("claim_category", "unknown") for c in sample)
    print("Claim category distribution in sample:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")

    designs = Counter(c.get("validation_design", "unknown") for c in sample)
    print("Validation design distribution in sample:")
    for design, count in designs.most_common():
        print(f"  {design}: {count}")

    print(f"\nInstructions:")
    print(f"1. Open {out_path} in a spreadsheet")
    print(f"2. For each row, open the PDF at pdf_path")
    print(f"3. Fill in human_claim_category (one of: {', '.join(CLAIM_TIERS)})")
    print(f"4. Fill in human_validation_design (one of: {', '.join(EVIDENCE_TIERS)})")
    print(f"5. Fill in human_sensitivity_correct (yes/no/na)")
    print(f"6. Add any notes in human_notes")
    print(f"7. Run: python generate_validation_sample.py --compute")


def compute_agreement():
    csv_path = DATA_DIR / "validation_sample.csv"
    if not csv_path.exists():
        print("No validation_sample.csv found. Run without --compute first.")
        return

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    filled = [r for r in rows if r["human_claim_category"].strip()]
    if not filled:
        print("No human judgments found. Fill in the human_* columns first.")
        return

    n = len(filled)
    print(f"Computing agreement on {n} devices...\n")

    # Claim category agreement
    claim_agree = sum(
        1 for r in filled
        if r["llm_claim_category"].strip().lower() == r["human_claim_category"].strip().lower()
    )
    claim_pct = claim_agree / n * 100

    # Validation design agreement
    design_filled = [r for r in filled if r["human_validation_design"].strip()]
    design_agree = sum(
        1 for r in design_filled
        if r["llm_validation_design"].strip().lower() == r["human_validation_design"].strip().lower()
    )
    design_pct = design_agree / len(design_filled) * 100 if design_filled else 0

    # Sensitivity correctness
    sens_filled = [r for r in filled if r["human_sensitivity_correct"].strip().lower() in ("yes", "no")]
    sens_correct = sum(1 for r in sens_filled if r["human_sensitivity_correct"].strip().lower() == "yes")
    sens_pct = sens_correct / len(sens_filled) * 100 if sens_filled else 0

    # Cohen's kappa for claim category
    claim_kappa = _compute_kappa(
        [r["llm_claim_category"].strip().lower() for r in filled],
        [r["human_claim_category"].strip().lower() for r in filled],
    )

    design_kappa = _compute_kappa(
        [r["llm_validation_design"].strip().lower() for r in design_filled],
        [r["human_validation_design"].strip().lower() for r in design_filled],
    ) if design_filled else 0

    print(f"CLAIM CATEGORY:")
    print(f"  Agreement: {claim_agree}/{n} ({claim_pct:.1f}%)")
    print(f"  Cohen's kappa: {claim_kappa:.3f}")
    print(f"\nVALIDATION DESIGN:")
    print(f"  Agreement: {design_agree}/{len(design_filled)} ({design_pct:.1f}%)")
    print(f"  Cohen's kappa: {design_kappa:.3f}")
    print(f"\nSENSITIVITY/SPECIFICITY CORRECTNESS:")
    print(f"  Correct: {sens_correct}/{len(sens_filled)} ({sens_pct:.1f}%)")

    print(f"\nKappa interpretation:")
    print(f"  0.81-1.00 = almost perfect")
    print(f"  0.61-0.80 = substantial")
    print(f"  0.41-0.60 = moderate")
    print(f"  0.21-0.40 = fair")

    # Save results
    results = {
        "n": n,
        "claim_agreement_pct": claim_pct,
        "claim_kappa": claim_kappa,
        "design_agreement_pct": design_pct,
        "design_kappa": design_kappa,
        "sensitivity_correctness_pct": sens_pct,
    }
    with open(DATA_DIR / "validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {DATA_DIR / 'validation_results.json'}")


def _compute_kappa(labels1: list, labels2: list) -> float:
    """Compute Cohen's kappa between two lists of labels."""
    if len(labels1) != len(labels2) or not labels1:
        return 0.0

    n = len(labels1)
    categories = sorted(set(labels1 + labels2))

    # Observed agreement
    agree = sum(1 for a, b in zip(labels1, labels2) if a == b)
    p_o = agree / n

    # Expected agreement
    p_e = 0
    for cat in categories:
        p1 = sum(1 for x in labels1 if x == cat) / n
        p2 = sum(1 for x in labels2 if x == cat) / n
        p_e += p1 * p2

    if p_e >= 1:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


if __name__ == "__main__":
    if "--compute" in sys.argv:
        compute_agreement()
    else:
        generate_sample()

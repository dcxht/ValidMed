"""Build the Claims-Evidence Proportionality Matrix from extracted claims data.

Maps each device's claim tier against its evidence tier to identify
disproportionate devices (high-impact claims with low-tier evidence).

Usage:
    python proportionality_matrix.py                    # From claims.json
    python proportionality_matrix.py data/claims.json   # Specific file
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
FIGURES_DIR = Path(__file__).parent.parent / "paper" / "figures"

# Ordered tiers (low to high)
CLAIM_TIERS = ["enhancement", "quantification", "detection", "triage", "diagnosis", "treatment"]
EVIDENCE_TIERS = ["none", "bench_only", "retrospective_single", "retrospective_multi", "prospective_single", "prospective_multi", "rct"]

CLAIM_LABELS = ["Enhancement", "Quantification", "Detection", "Triage", "Diagnosis", "Treatment"]
EVIDENCE_LABELS = ["None", "Bench\nOnly", "Retro\nSingle", "Retro\nMulti", "Prosp\nSingle", "Prosp\nMulti", "RCT"]

# Risk levels: claims above this line with evidence below this column are "disproportionate"
# Based on IMDRF SaMD risk categorization principles
CONCERN_THRESHOLD_CLAIM = 2   # detection and above
CONCERN_THRESHOLD_EVIDENCE = 2  # retrospective_single and above needed


def load_claims(path: str = None) -> list[dict]:
    path = path or str(DATA_DIR / "claims.json")
    with open(path) as f:
        return json.load(f)


def build_matrix(claims: list[dict]) -> np.ndarray:
    """Build the count matrix: rows = claim tiers, cols = evidence tiers."""
    matrix = np.zeros((len(CLAIM_TIERS), len(EVIDENCE_TIERS)), dtype=int)

    for c in claims:
        claim = (c.get("claim_category") or "").lower()
        evidence = (c.get("validation_design") or "").lower()

        if claim in CLAIM_TIERS and evidence in EVIDENCE_TIERS:
            row = CLAIM_TIERS.index(claim)
            col = EVIDENCE_TIERS.index(evidence)
            matrix[row][col] += 1

    return matrix


def compute_stats(claims: list[dict], matrix: np.ndarray) -> dict:
    """Compute key statistics from the proportionality matrix."""
    total = len(claims)
    total_in_matrix = matrix.sum()

    # Disproportionate: high-impact claim (detection+) with low evidence (none or bench_only)
    high_claim_low_evidence = 0
    for row_idx in range(CONCERN_THRESHOLD_CLAIM, len(CLAIM_TIERS)):
        for col_idx in range(0, CONCERN_THRESHOLD_EVIDENCE):
            high_claim_low_evidence += matrix[row_idx][col_idx]

    # Devices making diagnosis/treatment claims
    diagnosis_treatment = sum(
        1 for c in claims
        if (c.get("claim_category") or "").lower() in ("diagnosis", "treatment")
    )

    # Of those, how many have only bench or no evidence?
    dx_tx_low_evidence = sum(
        1 for c in claims
        if (c.get("claim_category") or "").lower() in ("diagnosis", "treatment")
        and (c.get("validation_design") or "").lower() in ("none", "bench_only")
    )

    # Triage devices with no prospective data
    triage_no_prospective = sum(
        1 for c in claims
        if (c.get("claim_category") or "").lower() == "triage"
        and (c.get("validation_design") or "").lower() not in ("prospective_single", "prospective_multi", "rct")
    )

    triage_total = sum(1 for c in claims if (c.get("claim_category") or "").lower() == "triage")

    # Has any performance metrics
    has_metrics = sum(
        1 for c in claims
        if any(c.get(m) for m in ["sensitivity", "specificity", "auc", "accuracy"])
    )

    return {
        "total_devices": total,
        "total_in_matrix": int(total_in_matrix),
        "high_claim_low_evidence": high_claim_low_evidence,
        "high_claim_low_evidence_pct": round(high_claim_low_evidence / total_in_matrix * 100, 1) if total_in_matrix else 0,
        "diagnosis_treatment_total": diagnosis_treatment,
        "diagnosis_treatment_low_evidence": dx_tx_low_evidence,
        "diagnosis_treatment_low_evidence_pct": round(dx_tx_low_evidence / diagnosis_treatment * 100, 1) if diagnosis_treatment else 0,
        "triage_total": triage_total,
        "triage_no_prospective": triage_no_prospective,
        "triage_no_prospective_pct": round(triage_no_prospective / triage_total * 100, 1) if triage_total else 0,
        "has_performance_metrics": has_metrics,
        "has_performance_metrics_pct": round(has_metrics / total * 100, 1),
    }


def plot_heatmap(matrix: np.ndarray, stats: dict):
    """Generate the proportionality matrix heatmap."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Color: white for 0, light blue for low counts, dark red for high counts
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", interpolation="nearest")

    # Add text annotations
    for i in range(len(CLAIM_TIERS)):
        for j in range(len(EVIDENCE_TIERS)):
            val = matrix[i][j]
            if val > 0:
                color = "white" if val > matrix.max() * 0.6 else "black"
                ax.text(j, i, str(val), ha="center", va="center", fontsize=11, fontweight="bold", color=color)

    # Draw the "concern zone" box (high claims, low evidence)
    from matplotlib.patches import Rectangle
    rect = Rectangle(
        (-0.5, CONCERN_THRESHOLD_CLAIM - 0.5),
        CONCERN_THRESHOLD_EVIDENCE, len(CLAIM_TIERS) - CONCERN_THRESHOLD_CLAIM,
        linewidth=2.5, edgecolor="red", facecolor="none", linestyle="--"
    )
    ax.add_patch(rect)
    ax.text(
        CONCERN_THRESHOLD_EVIDENCE / 2 - 0.5,
        len(CLAIM_TIERS) - 0.2,
        f"Concern Zone\n({stats['high_claim_low_evidence']} devices)",
        ha="center", va="bottom", fontsize=9, color="red", fontweight="bold"
    )

    ax.set_xticks(range(len(EVIDENCE_TIERS)))
    ax.set_xticklabels(EVIDENCE_LABELS, fontsize=9)
    ax.set_yticks(range(len(CLAIM_TIERS)))
    ax.set_yticklabels(CLAIM_LABELS, fontsize=10)

    ax.set_xlabel("Evidence Tier (from 510(k) submission)", fontsize=11, labelpad=10)
    ax.set_ylabel("Claim Tier (from intended use)", fontsize=11, labelpad=10)
    ax.set_title(
        f"Claims-Evidence Proportionality Matrix\n({stats['total_in_matrix']} FDA-Cleared AI/ML Devices)",
        fontsize=13, fontweight="bold", pad=15
    )

    plt.colorbar(im, ax=ax, label="Number of devices", shrink=0.8)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "proportionality_matrix.png", dpi=300)
    plt.savefig(FIGURES_DIR / "proportionality_matrix.pdf")
    plt.close()
    print(f"  Saved heatmap to {FIGURES_DIR / 'proportionality_matrix.png'}")


def print_report(claims: list[dict], matrix: np.ndarray, stats: dict):
    """Print the key findings."""
    print("\n" + "=" * 65)
    print("CLAIMS-EVIDENCE PROPORTIONALITY ANALYSIS")
    print("=" * 65)

    print(f"\nTotal devices with claims data: {stats['total_devices']}")
    print(f"Devices in matrix: {stats['total_in_matrix']}")
    print(f"Has performance metrics (sens/spec/AUC): {stats['has_performance_metrics']} ({stats['has_performance_metrics_pct']}%)")

    print(f"\n--- PROPORTIONALITY MATRIX ---")
    # Print text version
    header = f"{'':15s}" + "".join(f"{e:>10s}" for e in EVIDENCE_LABELS)
    print(header.replace('\n', ' '))
    for i, claim in enumerate(CLAIM_LABELS):
        row = f"{claim:15s}" + "".join(f"{matrix[i][j]:>10d}" for j in range(len(EVIDENCE_TIERS)))
        print(row)

    print(f"\n--- KEY FINDINGS ---")
    print(f"HIGH-IMPACT CLAIMS + LOW-TIER EVIDENCE (Concern Zone):")
    print(f"  {stats['high_claim_low_evidence']} devices ({stats['high_claim_low_evidence_pct']}%)")
    print(f"  These devices claim detection/triage/diagnosis/treatment")
    print(f"  but report only bench testing or no validation data")

    print(f"\nDIAGNOSIS/TREATMENT DEVICES:")
    print(f"  {stats['diagnosis_treatment_total']} total")
    print(f"  {stats['diagnosis_treatment_low_evidence']} ({stats['diagnosis_treatment_low_evidence_pct']}%) have only bench/no evidence")

    print(f"\nTRIAGE DEVICES:")
    print(f"  {stats['triage_total']} total")
    print(f"  {stats['triage_no_prospective']} ({stats['triage_no_prospective_pct']}%) have no prospective data")

    print("=" * 65)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    claims = load_claims(path)

    matrix = build_matrix(claims)
    stats = compute_stats(claims, matrix)

    print_report(claims, matrix, stats)
    plot_heatmap(matrix, stats)

    # Save stats
    with open(DATA_DIR / "proportionality_stats.json", "w") as f:
        json.dump(stats, f, indent=2, default=int)
    print(f"\n  Stats saved to {DATA_DIR / 'proportionality_stats.json'}")


if __name__ == "__main__":
    main()

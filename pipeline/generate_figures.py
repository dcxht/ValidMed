"""Generate publication-ready figures from ValidMed pipeline data."""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGURES_DIR = Path(__file__).parent.parent / "paper" / "figures"

TRUST_COLORS = {
    "strong": "#166534",
    "moderate": "#1e40af",
    "limited": "#854d0e",
    "none": "#991b1b",
}

TRUST_ORDER = ["strong", "moderate", "limited", "none"]
TRUST_LABELS = ["Strong", "Moderate", "Limited", "None"]


def load_data(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def fig1_trust_by_year(data: list[dict]):
    """Stacked bar: trust levels by clearance year."""
    by_year = defaultdict(lambda: Counter())
    for d in data:
        year = d.get("decision_date", "")[:4]
        if not year or int(year) < 2016:
            continue
        trust = d.get("score", {}).get("trust_level", "none")
        by_year[year][trust] += 1

    years = sorted(by_year.keys())
    fig, ax = plt.subplots(figsize=(10, 5))

    bottoms = [0] * len(years)
    for level, label in zip(TRUST_ORDER, TRUST_LABELS):
        values = [by_year[y][level] for y in years]
        ax.bar(years, values, bottom=bottoms, label=label,
               color=TRUST_COLORS[level], alpha=0.85)
        bottoms = [b + v for b, v in zip(bottoms, values)]

    ax.set_xlabel("Year of FDA Clearance")
    ax.set_ylabel("Number of Devices")
    ax.set_title("Evidence Levels of FDA-Cleared AI/ML Devices by Year")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_trust_by_year.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig1_trust_by_year.pdf")
    plt.close()
    print("  fig1_trust_by_year saved")


def fig2_trust_distribution(data: list[dict]):
    """Donut chart of trust level distribution."""
    trusts = Counter(d.get("score", {}).get("trust_level", "none") for d in data)

    fig, ax = plt.subplots(figsize=(6, 6))
    sizes = [trusts.get(level, 0) for level in TRUST_ORDER]
    colors = [TRUST_COLORS[level] for level in TRUST_ORDER]
    labels = [f"{label}\n{trusts.get(level,0)} ({trusts.get(level,0)/len(data)*100:.0f}%)"
              for level, label in zip(TRUST_ORDER, TRUST_LABELS)]

    wedges, texts = ax.pie(sizes, colors=colors, labels=labels,
                           startangle=90, wedgeprops={"width": 0.4, "edgecolor": "white"})

    for text in texts:
        text.set_fontsize(10)

    ax.set_title(f"Evidence Level Distribution\n({len(data)} FDA-Cleared AI/ML Devices)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_trust_distribution.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig2_trust_distribution.pdf")
    plt.close()
    print("  fig2_trust_distribution saved")


def fig3_zero_evidence_by_year(data: list[dict]):
    """Line chart: % devices with zero direct evidence by clearance year."""
    by_year = defaultdict(lambda: {"total": 0, "zero": 0})
    for d in data:
        year = d.get("decision_date", "")[:4]
        if not year or int(year) < 2016:
            continue
        by_year[year]["total"] += 1
        n_direct = d.get("score", {}).get("detail", {}).get("n_direct_publications", 0)
        if n_direct == 0:
            by_year[year]["zero"] += 1

    years = sorted(by_year.keys())
    pcts = [by_year[y]["zero"] / by_year[y]["total"] * 100 for y in years]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(years, pcts, "o-", color="#991b1b", linewidth=2, markersize=6)
    ax.set_xlabel("Year of FDA Clearance")
    ax.set_ylabel("% Devices with Zero Direct Evidence")
    ax.set_title("Proportion of AI/ML Devices Lacking Direct Published Evidence")
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color="#d1d5db", linestyle="--", alpha=0.5)

    for y, p in zip(years, pcts):
        ax.annotate(f"{p:.0f}%", (y, p), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_zero_evidence_trend.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig3_zero_evidence_trend.pdf")
    plt.close()
    print("  fig3_zero_evidence_trend saved")


def fig4_use_case_heatmap(data: list[dict]):
    """Horizontal bar: top 15 clinical use cases by evidence level."""
    from taxonomy import classify_device

    use_cases = defaultdict(lambda: Counter())
    for d in data:
        uc = classify_device(
            d.get("device_name", ""),
            d.get("product_code", ""),
            d.get("specialty_panel", ""),
        )
        trust = d.get("score", {}).get("trust_level", "none")
        use_cases[uc][trust] += 1

    # Top 15 by total count
    top = sorted(use_cases.items(), key=lambda x: sum(x[1].values()), reverse=True)[:15]
    top.reverse()  # Reverse for horizontal bar (top at top)

    fig, ax = plt.subplots(figsize=(10, 7))

    labels = [uc for uc, _ in top]
    lefts = [0] * len(top)

    for level, color_label in zip(TRUST_ORDER, TRUST_LABELS):
        values = [counts.get(level, 0) for _, counts in top]
        ax.barh(labels, values, left=lefts, label=color_label,
                color=TRUST_COLORS[level], alpha=0.85, height=0.7)
        lefts = [l + v for l, v in zip(lefts, values)]

    ax.set_xlabel("Number of Devices")
    ax.set_title("Evidence Levels by Clinical Use Case (Top 15)")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig4_use_case_evidence.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig4_use_case_evidence.pdf")
    plt.close()
    print("  fig4_use_case_evidence saved")


def generate_all(data_path: str):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data(data_path)
    print(f"Generating figures from {len(data)} devices...")

    fig1_trust_by_year(data)
    fig2_trust_distribution(data)
    fig3_zero_evidence_by_year(data)
    fig4_use_case_heatmap(data)

    print(f"\nAll figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_figures.py <enriched_json>")
        sys.exit(1)
    generate_all(sys.argv[1])

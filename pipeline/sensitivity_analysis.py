"""Sensitivity analysis: how do trust level distributions change under different thresholds?"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

SCENARIOS = {
    "base": {
        "description": "Current thresholds",
        "strong": lambda n, types: n >= 3 and ("RCT" in types or ("clinical_trial" in types and ("meta_analysis" in types or "systematic_review" in types))),
        "moderate": lambda n, types: n >= 3 or (n >= 2 and "clinical_trial" in types),
        "limited": lambda n, types: n >= 1,
    },
    "strict": {
        "description": "Strict: requires RCT for strong, clinical trial for moderate",
        "strong": lambda n, types: n >= 5 and "RCT" in types,
        "moderate": lambda n, types: n >= 3 and ("RCT" in types or "clinical_trial" in types),
        "limited": lambda n, types: n >= 2,
    },
    "lenient": {
        "description": "Lenient: lower thresholds",
        "strong": lambda n, types: n >= 2 and ("RCT" in types or "clinical_trial" in types),
        "moderate": lambda n, types: n >= 2,
        "limited": lambda n, types: n >= 1,
    },
    "count_only": {
        "description": "Count-only: ignores study types entirely",
        "strong": lambda n, types: n >= 5,
        "moderate": lambda n, types: n >= 3,
        "limited": lambda n, types: n >= 1,
    },
}


def classify(n_direct: int, study_types: set, scenario: dict) -> str:
    if n_direct == 0:
        return "none"
    if scenario["strong"](n_direct, study_types):
        return "strong"
    if scenario["moderate"](n_direct, study_types):
        return "moderate"
    if scenario["limited"](n_direct, study_types):
        return "limited"
    return "none"


def run_analysis(data_path: str):
    with open(data_path) as f:
        devices = json.load(f)

    total = len(devices)
    results = {}

    for name, scenario in SCENARIOS.items():
        counts = {"strong": 0, "moderate": 0, "limited": 0, "none": 0}

        for d in devices:
            evidence = d.get("evidence", [])
            direct = [e for e in evidence if e.get("match_tier") == "direct"]
            n_direct = len(direct)
            study_types = {e.get("study_type", "other") for e in direct}

            level = classify(n_direct, study_types, scenario)
            counts[level] += 1

        results[name] = {
            "description": scenario["description"],
            "counts": counts,
            "pcts": {k: round(v / total * 100, 1) for k, v in counts.items()},
        }

    # Print comparison table
    print(f"\nSensitivity Analysis — Trust Level Thresholds (N={total})")
    print("=" * 75)
    print(f"{'Scenario':15s} | {'Strong':>10s} | {'Moderate':>10s} | {'Limited':>10s} | {'None':>10s}")
    print("-" * 75)
    for name, r in results.items():
        p = r["pcts"]
        print(f"{name:15s} | {p['strong']:>8.1f}%  | {p['moderate']:>8.1f}%  | {p['limited']:>8.1f}%  | {p['none']:>8.1f}%")
    print("=" * 75)

    for name, r in results.items():
        print(f"\n  {name}: {r['description']}")

    # Save
    out = DATA_DIR / "sensitivity_analysis.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(DATA_DIR / "enriched_final.json")
    run_analysis(path)

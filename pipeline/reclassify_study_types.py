"""Re-classify study types in existing enriched data using the improved classifier.

This avoids re-running the full pipeline just to get better study type detection.
Applies title-based keyword fallback to catch RCTs, clinical trials, and meta-analyses
that PubMed's pubtype field missed.
"""

import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def classify(article: dict) -> str:
    """Improved study type classifier — uses pubtype + title keywords."""
    pub_types = [pt.lower() for pt in article.get("pubtype", [])]
    title = article.get("title", "").lower()

    # PubMed metadata first
    if "randomized controlled trial" in pub_types:
        return "RCT"
    if "clinical trial" in pub_types or any("clinical trial" in pt for pt in pub_types):
        return "clinical_trial"
    if "meta-analysis" in pub_types:
        return "meta_analysis"
    if "systematic review" in pub_types:
        return "systematic_review"

    # Title-based fallback
    if any(kw in title for kw in ("randomized", "randomised", "rct", "random assignment")):
        return "RCT"
    if any(kw in title for kw in ("clinical trial", "pivotal trial", "pivotal study",
                                   "prospective trial", "multicenter trial",
                                   "multicentre trial", "registration trial")):
        return "clinical_trial"
    if any(kw in title for kw in ("meta-analysis", "meta analysis", "metaanalysis")):
        return "meta_analysis"
    if any(kw in title for kw in ("systematic review", "scoping review")):
        return "systematic_review"
    if any(kw in title for kw in ("prospective", "validation study", "clinical validation",
                                   "clinical evaluation", "clinical performance",
                                   "diagnostic accuracy", "real-world")):
        return "clinical_study"

    if "review" in pub_types:
        return "review"
    if "case reports" in pub_types:
        return "case_report"
    if "validation study" in pub_types or "comparative study" in pub_types:
        return "clinical_study"

    return "other"


def reclassify(data_path: str):
    with open(data_path) as f:
        devices = json.load(f)

    changed = 0
    upgrades = {"other_to_rct": 0, "other_to_clinical": 0, "other_to_meta": 0,
                "other_to_systematic": 0, "other_to_clinical_study": 0}

    for device in devices:
        for article in device.get("evidence", []):
            old = article.get("study_type", "other")
            new = classify(article)
            if old != new:
                article["study_type"] = new
                changed += 1
                key = f"{old}_to_{new}"
                if key in upgrades:
                    upgrades[key] += 1

    # Recompute scores with new study types
    from score import compute_score
    for device in devices:
        evidence = device.get("evidence", [])
        safety = device.get("safety_events", [])
        recalls = device.get("recalls", [])
        trials = device.get("trials", [])
        device["score"] = compute_score(evidence, safety, recalls, trials)

    # Save
    out_path = Path(data_path)
    with open(out_path, "w") as f:
        json.dump(devices, f, indent=2, default=str)

    print(f"Reclassified {changed} articles in {len(devices)} devices")
    for k, v in upgrades.items():
        if v > 0:
            print(f"  {k}: {v}")

    # Print new trust level distribution
    from collections import Counter
    trusts = Counter(d["score"]["trust_level"] for d in devices)
    print(f"\nUpdated trust levels:")
    for level in ["strong", "moderate", "limited", "none"]:
        n = trusts.get(level, 0)
        print(f"  {level}: {n} ({n/len(devices)*100:.1f}%)")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(DATA_DIR / "enriched_final.json")
    reclassify(path)

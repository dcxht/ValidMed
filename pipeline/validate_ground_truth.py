#!/usr/bin/env python3
"""
Validate ValidMed pipeline output against hand-curated ground truth
for 20 well-known FDA-cleared AI devices.
"""

import json
import glob
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---------------------------------------------------------------------------
# Ground truth: 20 well-documented FDA-cleared AI/ML devices
# pub_count_min: conservative lower bound on known publications
# expected_trust: what a well-calibrated pipeline should assign
# ---------------------------------------------------------------------------
GROUND_TRUTH = [
    {
        "device_name": "IDx-DR",
        "company": "Digital Diagnostics",
        "alt_names": ["idx-dr", "idx dr"],
        "alt_companies": ["digital diagnostics", "de novo"],
        "expected_pub_count_min": 15,
        "expected_study_types": ["rct", "clinical_trial"],
        "expected_trust": "strong",
    },
    {
        "device_name": "Viz LVO",
        "company": "Viz.ai",
        "alt_names": ["viz lvo", "viz.ai lvo"],
        "alt_companies": ["viz.ai", "viz ai"],
        "expected_pub_count_min": 15,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "strong",
    },
    {
        "device_name": "Caption Guidance",
        "company": "Caption Health",
        "alt_names": ["caption guidance", "caption ai"],
        "alt_companies": ["caption health"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "Aidoc BriefCase",
        "company": "Aidoc Medical",
        "alt_names": ["briefcase", "aidoc briefcase", "aidoc"],
        "alt_companies": ["aidoc", "aidoc medical"],
        "expected_pub_count_min": 10,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "GI Genius",
        "company": "Medtronic",
        "alt_names": ["gi genius", "gi-genius", "genius"],
        "alt_companies": ["medtronic", "cosmo pharmaceuticals", "cosmo"],
        "expected_pub_count_min": 15,
        "expected_study_types": ["rct", "clinical_trial"],
        "expected_trust": "strong",
    },
    {
        "device_name": "Arterys Cardio AI",
        "company": "Arterys",
        "alt_names": ["cardio ai", "arterys"],
        "alt_companies": ["arterys", "tempus"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "RAPID LVO",
        "company": "iSchemaView",
        "alt_names": ["rapid lvo", "rapid ctp", "rapid"],
        "alt_companies": ["ischemaview", "rapidai"],
        "expected_pub_count_min": 20,
        "expected_study_types": ["rct", "clinical_trial"],
        "expected_trust": "strong",
    },
    {
        "device_name": "Paige Prostate",
        "company": "Paige AI",
        "alt_names": ["paige prostate", "paige"],
        "alt_companies": ["paige ai", "paige.ai", "paige"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "QuantX",
        "company": "Qlarity Imaging",
        "alt_names": ["quantx"],
        "alt_companies": ["qlarity", "qlarity imaging"],
        "expected_pub_count_min": 3,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "ContaCT",
        "company": "Viz.ai",
        "alt_names": ["contact", "contac t"],
        "alt_companies": ["viz.ai", "viz ai"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "Zebra Medical",
        "company": "Zebra Medical Vision",
        "alt_names": ["zebra", "zebra-med"],
        "alt_companies": ["zebra medical", "zebra medical vision", "zebra-med"],
        "expected_pub_count_min": 10,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "HeartFlow FFRct",
        "company": "HeartFlow",
        "alt_names": ["heartflow", "ffrct", "heartflow ffrct", "heartflow analysis"],
        "alt_companies": ["heartflow"],
        "expected_pub_count_min": 25,
        "expected_study_types": ["rct", "clinical_trial"],
        "expected_trust": "strong",
    },
    {
        "device_name": "Apple ECG",
        "company": "Apple",
        "alt_names": ["ecg app", "apple ecg", "irregular rhythm notification"],
        "alt_companies": ["apple"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "KardiaMobile",
        "company": "AliveCor",
        "alt_names": ["kardiamobile", "kardia", "kardia mobile"],
        "alt_companies": ["alivecor", "alive cor"],
        "expected_pub_count_min": 10,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "BriefCase for PE",
        "company": "Aidoc",
        "alt_names": ["briefcase", "pe triage", "aidoc pe"],
        "alt_companies": ["aidoc", "aidoc medical"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "OsteoDetect",
        "company": "Imagen Technologies",
        "alt_names": ["osteodetect", "imagen osteodetect"],
        "alt_companies": ["imagen", "imagen technologies"],
        "expected_pub_count_min": 3,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "limited",
    },
    {
        "device_name": "Lunit INSIGHT CXR",
        "company": "Lunit",
        "alt_names": ["lunit insight", "insight cxr", "lunit"],
        "alt_companies": ["lunit"],
        "expected_pub_count_min": 10,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "qXR",
        "company": "Qure.ai",
        "alt_names": ["qxr", "qure"],
        "alt_companies": ["qure.ai", "qure ai", "qure"],
        "expected_pub_count_min": 10,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
    {
        "device_name": "SubtleMR",
        "company": "Subtle Medical",
        "alt_names": ["subtlemr", "subtle mr"],
        "alt_companies": ["subtle medical"],
        "expected_pub_count_min": 3,
        "expected_study_types": ["other"],
        "expected_trust": "limited",
    },
    {
        "device_name": "EchoGo",
        "company": "Ultromics",
        "alt_names": ["echogo", "echo go"],
        "alt_companies": ["ultromics"],
        "expected_pub_count_min": 5,
        "expected_study_types": ["clinical_trial"],
        "expected_trust": "moderate",
    },
]


def load_latest_enriched():
    """Find and load the latest enriched data file."""
    candidates = []

    final = os.path.join(DATA_DIR, "enriched_final.json")
    if os.path.exists(final):
        candidates.append(final)

    checkpoints = sorted(glob.glob(os.path.join(DATA_DIR, "enriched_checkpoint_*.json")))
    candidates.extend(checkpoints)

    if not candidates:
        raise FileNotFoundError("No enriched data files found in " + DATA_DIR)

    # Prefer enriched_final, otherwise latest checkpoint
    chosen = candidates[-1] if not os.path.exists(final) else final
    print(f"Loading enriched data from: {chosen}")

    with open(chosen) as f:
        return json.load(f)


def normalize(s):
    """Lowercase and strip for fuzzy matching."""
    return s.lower().strip()


def find_device_in_pipeline(gt_entry, pipeline_devices):
    """
    Try to match a ground truth device against the pipeline output.
    Returns list of matching pipeline entries (could match multiple clearances).
    """
    matches = []
    gt_name_lower = normalize(gt_entry["device_name"])
    gt_alt_names = [normalize(n) for n in gt_entry.get("alt_names", [])]
    gt_alt_companies = [normalize(c) for c in gt_entry.get("alt_companies", [])]

    for dev in pipeline_devices:
        dev_name = normalize(dev.get("device_name", ""))
        dev_company = normalize(dev.get("company", ""))

        # Check device name match
        name_match = False
        if gt_name_lower in dev_name or dev_name in gt_name_lower:
            name_match = True
        for alt in gt_alt_names:
            if alt in dev_name or dev_name in alt:
                name_match = True
                break

        # Check company match
        company_match = False
        if normalize(gt_entry["company"]) in dev_company or dev_company in normalize(gt_entry["company"]):
            company_match = True
        for alt in gt_alt_companies:
            if alt in dev_company or dev_company in alt:
                company_match = True
                break

        if name_match or company_match:
            matches.append(dev)

    return matches


def evaluate(gt_entry, pipeline_matches):
    """
    Compare pipeline output for a device against ground truth expectations.
    Returns a result dict.
    """
    result = {
        "gt_device": gt_entry["device_name"],
        "gt_company": gt_entry["company"],
        "gt_expected_trust": gt_entry["expected_trust"],
        "gt_expected_pub_min": gt_entry["expected_pub_count_min"],
        "gt_expected_study_types": gt_entry["expected_study_types"],
        "found_in_pipeline": len(pipeline_matches) > 0,
        "n_pipeline_matches": len(pipeline_matches),
        "issues": [],
    }

    if not pipeline_matches:
        result["issues"].append("NOT_FOUND: Device not found in pipeline output")
        result["pipeline_pub_count"] = 0
        result["pipeline_trust"] = None
        result["pipeline_study_types"] = []
        return result

    # Aggregate across all matching entries (some devices have multiple clearances)
    all_evidence = []
    trust_levels = []
    total_direct_pubs = 0

    for dev in pipeline_matches:
        evidence = dev.get("evidence", [])
        all_evidence.extend(evidence)
        score = dev.get("score", {})
        trust_levels.append(score.get("trust_level", "none"))
        detail = score.get("detail", {})
        total_direct_pubs += detail.get("n_direct_publications", 0)

    # Deduplicate evidence by PMID
    seen_pmids = set()
    unique_evidence = []
    for e in all_evidence:
        pmid = e.get("pmid")
        if pmid and pmid not in seen_pmids:
            seen_pmids.add(pmid)
            unique_evidence.append(e)

    pipeline_pub_count = len(unique_evidence)
    pipeline_study_types = list(set(e.get("study_type", "other") for e in unique_evidence))

    # Best trust level across matches
    trust_rank = {"strong": 4, "moderate": 3, "limited": 2, "none": 1}
    best_trust = max(trust_levels, key=lambda t: trust_rank.get(t, 0))

    result["pipeline_pub_count"] = pipeline_pub_count
    result["pipeline_direct_pubs"] = total_direct_pubs
    result["pipeline_trust"] = best_trust
    result["pipeline_study_types"] = pipeline_study_types
    result["pipeline_device_names"] = [d["device_name"] for d in pipeline_matches]

    # --- Check: publication count ---
    if pipeline_pub_count < gt_entry["expected_pub_count_min"]:
        result["issues"].append(
            f"LOW_PUB_COUNT: pipeline found {pipeline_pub_count} pubs, "
            f"expected >= {gt_entry['expected_pub_count_min']}"
        )

    # --- Check: trust level ---
    expected_rank = trust_rank.get(gt_entry["expected_trust"], 0)
    actual_rank = trust_rank.get(best_trust, 0)
    if actual_rank < expected_rank:
        result["issues"].append(
            f"TRUST_UNDERRATED: pipeline says '{best_trust}', "
            f"expected '{gt_entry['expected_trust']}'"
        )
    elif actual_rank > expected_rank:
        result["issues"].append(
            f"TRUST_OVERRATED: pipeline says '{best_trust}', "
            f"expected '{gt_entry['expected_trust']}'"
        )

    # --- Check: study types ---
    for expected_type in gt_entry["expected_study_types"]:
        if expected_type not in pipeline_study_types:
            result["issues"].append(
                f"MISSING_STUDY_TYPE: expected '{expected_type}' not found in pipeline output"
            )

    return result


def compute_metrics(results):
    """Compute precision/recall style metrics across all ground truth devices."""
    total = len(results)
    found = sum(1 for r in results if r["found_in_pipeline"])
    trust_correct = sum(
        1 for r in results
        if r["found_in_pipeline"] and r["pipeline_trust"] == r["gt_expected_trust"]
    )
    trust_within_one = sum(
        1 for r in results
        if r["found_in_pipeline"]
        and abs(
            {"strong": 4, "moderate": 3, "limited": 2, "none": 1}.get(r["pipeline_trust"], 0)
            - {"strong": 4, "moderate": 3, "limited": 2, "none": 1}.get(r["gt_expected_trust"], 0)
        ) <= 1
    )
    pub_adequate = sum(
        1 for r in results
        if r["found_in_pipeline"] and r["pipeline_pub_count"] >= r["gt_expected_pub_min"]
    )

    metrics = {
        "total_ground_truth_devices": total,
        "found_in_pipeline": found,
        "recall_device_match": round(found / total, 3) if total else 0,
        "trust_exact_match": trust_correct,
        "trust_exact_match_rate": round(trust_correct / found, 3) if found else 0,
        "trust_within_one_level": trust_within_one,
        "trust_within_one_rate": round(trust_within_one / found, 3) if found else 0,
        "pub_count_adequate": pub_adequate,
        "pub_count_adequate_rate": round(pub_adequate / found, 3) if found else 0,
    }
    return metrics


def main():
    pipeline_devices = load_latest_enriched()
    print(f"Pipeline contains {len(pipeline_devices)} devices\n")

    results = []
    for gt in GROUND_TRUTH:
        matches = find_device_in_pipeline(gt, pipeline_devices)
        result = evaluate(gt, matches)
        results.append(result)

        status = "OK" if not result["issues"] else "ISSUES"
        icon = " " if status == "OK" else "!"
        print(f"[{icon}] {gt['device_name']:30s} | found={result['found_in_pipeline']:<5} "
              f"| pubs={result['pipeline_pub_count']:>3} (expect>={gt['expected_pub_count_min']:>2}) "
              f"| trust={str(result['pipeline_trust']):>8} (expect={gt['expected_trust']})")
        for issue in result["issues"]:
            print(f"     -> {issue}")

    metrics = compute_metrics(results)

    print("\n" + "=" * 70)
    print("VALIDATION METRICS")
    print("=" * 70)
    print(f"  Device recall (found/total):   {metrics['found_in_pipeline']}/{metrics['total_ground_truth_devices']} = {metrics['recall_device_match']:.1%}")
    print(f"  Trust exact match rate:        {metrics['trust_exact_match']}/{metrics['found_in_pipeline']} = {metrics['trust_exact_match_rate']:.1%}")
    print(f"  Trust within 1 level rate:     {metrics['trust_within_one_level']}/{metrics['found_in_pipeline']} = {metrics['trust_within_one_rate']:.1%}")
    print(f"  Pub count adequate rate:       {metrics['pub_count_adequate']}/{metrics['found_in_pipeline']} = {metrics['pub_count_adequate_rate']:.1%}")

    # Build output report
    report = {
        "generated_at": datetime.now().isoformat(),
        "source_file": os.path.basename(
            glob.glob(os.path.join(DATA_DIR, "enriched_*.json"))[-1]
        ),
        "pipeline_device_count": len(pipeline_devices),
        "ground_truth_device_count": len(GROUND_TRUTH),
        "metrics": metrics,
        "device_results": results,
    }

    out_path = os.path.join(DATA_DIR, "validation_report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()

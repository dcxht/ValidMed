"""Export enriched pipeline data to static JSON files for the web frontend."""

import json
import sys
from datetime import date
from pathlib import Path

from taxonomy import classify_device


def _compute_trust(evidence: list, n_direct: int, trials: list) -> str:
    """Compute trust level from evidence data.

    Uses only reliably available data — no is_manufacturer_authored.
    """
    if not evidence:
        return "none"

    direct = [e for e in evidence if e.get("match_tier") == "direct"]
    direct_types = {e.get("study_type") for e in direct}
    has_rct = "RCT" in direct_types
    has_clinical = "clinical_trial" in direct_types or "clinical_study" in direct_types or has_rct
    has_meta = "meta_analysis" in direct_types or "systematic_review" in direct_types
    trial_results = any(t.get("has_results") for t in trials)

    if n_direct >= 3 and (has_rct or (has_clinical and has_meta) or trial_results):
        return "strong"
    if n_direct >= 3:
        return "moderate"
    if n_direct >= 2 and has_clinical:
        return "moderate"
    if n_direct >= 1:
        return "limited"
    if evidence:
        return "limited"
    return "none"

WEB_PUBLIC = Path(__file__).parent.parent / "web" / "public" / "data"


def _years_since(decision_date: str) -> float | None:
    """Calculate years since clearance date."""
    if not decision_date or len(decision_date) < 10:
        return None
    try:
        parts = decision_date.split("-")
        cleared = date(int(parts[0]), int(parts[1]), int(parts[2]))
        delta = date.today() - cleared
        return round(delta.days / 365.25, 1)
    except (ValueError, IndexError):
        return None


def export_static(enriched_path: str):
    with open(enriched_path) as f:
        enriched = json.load(f)

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)

    # Devices summary (for the table view)
    devices = []
    for i, d in enumerate(enriched, start=1):
        detail = d.get("score", {}).get("detail", {})
        n_pubmed = detail.get("n_publications", 0)
        ss_evidence = d.get("evidence_semantic_scholar", [])
        oa_evidence = d.get("evidence_openalex", [])
        n_ss = len(ss_evidence)
        n_oa = len(oa_evidence)
        has_regulatory = bool(d.get("regulatory_evidence", {}).get("has_clinical_data"))
        has_family_ev = d.get("family_evidence", {}).get("inherited_publication_count", 0) > 0
        has_denovo = bool(d.get("denovo_summary"))
        clearance_details = d.get("clearance_details", {})
        decision_date = d.get("decision_date")

        # Count evidence by match tier
        evidence_list = d.get("evidence", [])
        n_direct = sum(1 for e in evidence_list if e.get("match_tier") == "direct")
        n_company = sum(1 for e in evidence_list if e.get("match_tier") == "company")

        devices.append({
            "id": i,
            "fda_submission_number": d.get("fda_submission_number"),
            "device_name": d.get("device_name"),
            "company": d.get("company"),
            "decision_date": decision_date,
            "specialty_panel": d.get("specialty_panel"),
            "product_code": d.get("product_code"),
            "device_class": d.get("device_class") or clearance_details.get("device_class"),
            "clinical_use_case": classify_device(
                d.get("device_name", ""),
                d.get("product_code", ""),
                d.get("specialty_panel", ""),
            ),
            "trust_level": _compute_trust(evidence_list, n_direct, d.get("trials", [])),
            "evidence_score": d.get("score", {}).get("total", 0),
            "evidence_count": n_pubmed,
            "evidence_direct": n_direct,
            "evidence_company": n_company,
            "evidence_count_ss": n_ss,
            "evidence_count_oa": n_oa,
            "evidence_total": n_pubmed + n_ss + n_oa,
            "has_regulatory_data": has_regulatory,
            "has_family_evidence": has_family_ev,
            "has_denovo_summary": has_denovo,
            "any_evidence": (n_pubmed + n_ss + n_oa) > 0 or has_regulatory or has_family_ev,
            "safety_event_count": d.get("score", {}).get("detail", {}).get("n_safety_events", 0),
            "recall_count": d.get("score", {}).get("detail", {}).get("n_recalls", 0),
            "trial_count": d.get("score", {}).get("detail", {}).get("n_trials", 0),
            "has_fda_summary": clearance_details.get("statement_or_summary") == "Summary",
            "fda_summary_url": clearance_details.get("summary_url"),
            "years_since_clearance": _years_since(decision_date),
            "clearance_year": decision_date[:4] if decision_date and len(decision_date) >= 4 else None,
        })

    with open(WEB_PUBLIC / "devices.json", "w") as f:
        json.dump(devices, f)

    # Individual device detail files
    details_dir = WEB_PUBLIC / "devices"
    details_dir.mkdir(exist_ok=True)
    for i, d in enumerate(enriched, start=1):
        detail = {
            **devices[i - 1],
            "score_breakdown": d.get("score", {}),
            "clearance_details": d.get("clearance_details", {}),
            "evidence": d.get("evidence", []),
            "evidence_semantic_scholar": d.get("evidence_semantic_scholar", []),
            "evidence_openalex": d.get("evidence_openalex", []),
            "regulatory_evidence": d.get("regulatory_evidence", {}),
            "family_evidence": d.get("family_evidence", {}),
            "denovo_summary": d.get("denovo_summary", {}),
            "safety_events": d.get("safety_events", []),
            "recalls": d.get("recalls", []),
            "trials": d.get("trials", []),
        }
        with open(details_dir / f"{i}.json", "w") as f:
            json.dump(detail, f)

    # Aggregate stats for the dashboard
    stats = _compute_aggregate_stats(devices)
    with open(WEB_PUBLIC / "stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Exported {len(devices)} devices to {WEB_PUBLIC}")
    print(f"  devices.json: {(WEB_PUBLIC / 'devices.json').stat().st_size / 1024:.0f} KB")
    print(f"  stats.json: aggregate dashboard stats")


def _compute_aggregate_stats(devices: list[dict]) -> dict:
    """Compute aggregate stats for the dashboard."""
    total = len(devices)
    if total == 0:
        return {}

    zero_pubmed = sum(1 for d in devices if d["evidence_count"] == 0)
    zero_all = sum(1 for d in devices if d["evidence_total"] == 0)
    has_events = sum(1 for d in devices if d["safety_event_count"] > 0)
    has_recalls = sum(1 for d in devices if d["recall_count"] > 0)
    has_summary = sum(1 for d in devices if d["has_fda_summary"])
    avg_score = sum(d["evidence_score"] for d in devices) / total

    # By clearance year
    by_year = {}
    for d in devices:
        year = d.get("clearance_year")
        if not year:
            continue
        if year not in by_year:
            by_year[year] = {"total": 0, "zero_evidence": 0}
        by_year[year]["total"] += 1
        if d["evidence_total"] == 0:
            by_year[year]["zero_evidence"] += 1

    # By specialty
    by_specialty = {}
    for d in devices:
        spec = d.get("specialty_panel", "Unknown")
        if spec not in by_specialty:
            by_specialty[spec] = {"total": 0, "zero_evidence": 0, "avg_score": 0, "total_score": 0}
        by_specialty[spec]["total"] += 1
        by_specialty[spec]["total_score"] += d["evidence_score"]
        if d["evidence_total"] == 0:
            by_specialty[spec]["zero_evidence"] += 1

    for spec in by_specialty:
        n = by_specialty[spec]["total"]
        by_specialty[spec]["avg_score"] = round(by_specialty[spec]["total_score"] / n, 1)
        del by_specialty[spec]["total_score"]

    # By device class
    by_class = {}
    for d in devices:
        dc = d.get("device_class", "Unknown")
        if dc not in by_class:
            by_class[dc] = {"total": 0, "zero_evidence": 0}
        by_class[dc]["total"] += 1
        if d["evidence_total"] == 0:
            by_class[dc]["zero_evidence"] += 1

    return {
        "total_devices": total,
        "zero_pubmed_evidence": zero_pubmed,
        "zero_pubmed_evidence_pct": round(zero_pubmed / total * 100, 1),
        "zero_all_evidence": zero_all,
        "zero_all_evidence_pct": round(zero_all / total * 100, 1),
        "has_adverse_events": has_events,
        "has_recalls": has_recalls,
        "has_fda_summary": has_summary,
        "avg_evidence_score": round(avg_score, 1),
        "by_year": dict(sorted(by_year.items())),
        "by_specialty": by_specialty,
        "by_device_class": by_class,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_static.py <enriched_json_path>")
        sys.exit(1)
    export_static(sys.argv[1])

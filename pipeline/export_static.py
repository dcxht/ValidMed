"""Export enriched pipeline data to static JSON files for the web frontend."""

import json
import sys
from datetime import date
from pathlib import Path

from taxonomy import classify_device


# Claim categories considered high-impact for concern zone calculation
HIGH_IMPACT_CLAIMS = {"detection", "triage", "diagnosis", "treatment"}
# Validation designs considered low-tier
LOW_TIER_EVIDENCE = {"none", "bench_only"}


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


def _load_claims(pipeline_dir: Path) -> dict:
    """Load claims.json and index by k_number."""
    claims_path = pipeline_dir / "data" / "claims.json"
    if not claims_path.exists():
        print(f"Warning: {claims_path} not found, skipping claims merge")
        return {}
    with open(claims_path) as f:
        claims = json.load(f)
    return {c["k_number"]: c for c in claims if c.get("k_number")}


def export_static(enriched_path: str):
    with open(enriched_path) as f:
        enriched = json.load(f)

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)

    # Load claims data for merging
    pipeline_dir = Path(__file__).parent
    claims_lookup = _load_claims(pipeline_dir)

    # Devices summary (for the table view)
    devices = []
    for i, d in enumerate(enriched, start=1):
        detail = d.get("score", {}).get("detail", {})
        clearance_details = d.get("clearance_details", {})
        decision_date = d.get("decision_date")
        k_number = d.get("fda_submission_number")

        # Merge claims data
        claim = claims_lookup.get(k_number, {})
        claim_category = claim.get("claim_category")
        validation_design = claim.get("validation_design")
        is_concern_zone = (
            claim_category in HIGH_IMPACT_CLAIMS
            and validation_design in LOW_TIER_EVIDENCE
        )

        # Performance metrics from claims (replaces old values)
        sensitivity = claim.get("sensitivity")
        specificity = claim.get("specificity")
        auc = claim.get("auc")
        sample_size = claim.get("sample_size")
        num_sites = claim.get("num_sites")
        intended_use_raw = claim.get("intended_use") or ""
        intended_use = intended_use_raw[:200] if intended_use_raw else None
        autonomous_or_assistive = claim.get("autonomous_or_assistive")

        devices.append({
            "id": i,
            "fda_submission_number": k_number,
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
            # Claims-evidence proportionality fields
            "claim_category": claim_category,
            "validation_design": validation_design,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "auc": auc,
            "sample_size": sample_size,
            "num_sites": num_sites,
            "intended_use": intended_use,
            "autonomous_or_assistive": autonomous_or_assistive,
            "is_concern_zone": is_concern_zone,
            # Safety
            "safety_event_count": detail.get("n_safety_events", 0),
            "recall_count": detail.get("n_recalls", 0),
            # Clearance
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
        k_number = d.get("fda_submission_number")
        claim = claims_lookup.get(k_number, {})

        detail = {
            **devices[i - 1],
            "clearance_details": d.get("clearance_details", {}),
            # Claims extraction: full intended_use for detail view
            "intended_use_full": claim.get("intended_use"),
            "target_condition": claim.get("target_condition"),
            "ground_truth": claim.get("ground_truth"),
            "other_metrics": claim.get("other_metrics"),
            # Safety data
            "safety_events": d.get("safety_events", []),
            "recalls": d.get("recalls", []),
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

    concern_zone = sum(1 for d in devices if d.get("is_concern_zone"))
    bench_only = sum(1 for d in devices if d.get("validation_design") in ("none", "bench_only"))
    has_metrics = sum(1 for d in devices if any(d.get(m) is not None for m in ("sensitivity", "specificity", "auc")))
    has_events = sum(1 for d in devices if d["safety_event_count"] > 0)
    has_recalls = sum(1 for d in devices if d["recall_count"] > 0)

    # By claim category
    by_claim = {}
    for d in devices:
        cat = d.get("claim_category") or "no_pdf"
        if cat not in by_claim:
            by_claim[cat] = {"total": 0, "concern_zone": 0}
        by_claim[cat]["total"] += 1
        if d.get("is_concern_zone"):
            by_claim[cat]["concern_zone"] += 1

    # By validation design
    by_validation = {}
    for d in devices:
        vd = d.get("validation_design") or "no_pdf"
        if vd not in by_validation:
            by_validation[vd] = 0
        by_validation[vd] += 1

    # By clearance year
    by_year = {}
    for d in devices:
        year = d.get("clearance_year")
        if not year:
            continue
        if year not in by_year:
            by_year[year] = {"total": 0, "concern_zone": 0}
        by_year[year]["total"] += 1
        if d.get("is_concern_zone"):
            by_year[year]["concern_zone"] += 1

    # By specialty
    by_specialty = {}
    for d in devices:
        spec = d.get("specialty_panel", "Unknown")
        if spec not in by_specialty:
            by_specialty[spec] = {"total": 0, "concern_zone": 0}
        by_specialty[spec]["total"] += 1
        if d.get("is_concern_zone"):
            by_specialty[spec]["concern_zone"] += 1

    devices_with_claims = sum(1 for d in devices if d.get("claim_category") and d["claim_category"] != "no_pdf")

    return {
        "total_devices": total,
        "devices_with_claims": devices_with_claims,
        "concern_zone": concern_zone,
        "concern_zone_pct": round(concern_zone / devices_with_claims * 100, 1) if devices_with_claims else 0,
        "bench_only": bench_only,
        "bench_only_pct": round(bench_only / devices_with_claims * 100, 1) if devices_with_claims else 0,
        "has_performance_metrics": has_metrics,
        "has_performance_metrics_pct": round(has_metrics / devices_with_claims * 100, 1) if devices_with_claims else 0,
        "has_adverse_events": has_events,
        "has_recalls": has_recalls,
        "by_claim_category": by_claim,
        "by_validation_design": by_validation,
        "by_year": dict(sorted(by_year.items())),
        "by_specialty": by_specialty,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_static.py <enriched_json_path>")
        sys.exit(1)
    export_static(sys.argv[1])

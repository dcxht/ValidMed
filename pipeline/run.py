"""Main pipeline: parse FDA list, enrich from all sources, compute scores, upload."""

import json
import sys
import time
from pathlib import Path

import enrich_openfda
import enrich_pubmed
import enrich_trials
import score
from parse_fda_list import parse_fda_excel

DATA_DIR = Path(__file__).parent / "data"


def run_pipeline(excel_path: str, limit: int | None = None, upload: bool = False, resume: str | None = None):
    """Run the full enrichment pipeline.

    Args:
        excel_path: Path to the FDA AI/ML device Excel file.
        limit: Process only the first N devices (for testing).
        upload: If True, upload results to Supabase.
        resume: Path to a checkpoint JSON to resume from.
    """
    # Step 1: Parse FDA device list
    print("Parsing FDA device list...")
    devices = parse_fda_excel(excel_path)
    print(f"  Found {len(devices)} devices")

    if limit:
        devices = devices[:limit]
        print(f"  Limited to first {limit} devices")

    # Resume from checkpoint if provided
    enriched = []
    start_idx = 0
    if resume:
        with open(resume) as f:
            enriched = json.load(f)
        seen = {d["fda_submission_number"] for d in enriched}
        start_idx = len(enriched)
        print(f"  Resuming from checkpoint: {start_idx} devices already processed")

    # Step 2: Enrich each device
    for i, device in enumerate(devices):
        if i < start_idx:
            continue
        name = device.get("device_name", "")
        company = device.get("company", "")
        k_number = device.get("fda_submission_number", "")
        specialty = device.get("specialty_panel", "")

        print(f"  [{i+1}/{len(devices)}] {name} ({company})", flush=True)

        # Retry wrapper for transient network errors
        evidence = []
        fda_data = {"safety_events": [], "recalls": []}
        trials = []

        for attempt in range(3):
            try:
                evidence = enrich_pubmed.enrich_device(name, company, specialty)
                fda_data = enrich_openfda.enrich_device(k_number, name, company)
                # ClinicalTrials.gov runs as separate pass (enrich_trials.py)
                # to avoid 403 slowdowns in environments where it's blocked
                trials = []
                break
            except Exception as e:
                print(f"    Retry {attempt+1}/3: {e}", flush=True)
                time.sleep(2 ** attempt)

        # Score
        device_score = score.compute_score(
            evidence, fda_data["safety_events"], fda_data["recalls"], trials
        )

        enriched.append({
            **device,
            "evidence": evidence,
            "safety_events": fda_data["safety_events"],
            "recalls": fda_data["recalls"],
            "trials": trials,
            "score": device_score,
        })

        # Progress save every 50 devices
        if (i + 1) % 50 == 0:
            _save_progress(enriched, i + 1)

    # Step 3: Save results
    _save_progress(enriched, len(enriched), final=True)

    # Step 4: Upload to Supabase
    if upload:
        upload_to_supabase(enriched)

    # Step 5: Print summary stats
    _print_summary(enriched)

    return enriched


def _save_progress(enriched: list, count: int, final: bool = False):
    DATA_DIR.mkdir(exist_ok=True)
    suffix = "final" if final else f"checkpoint_{count}"
    out_path = DATA_DIR / f"enriched_{suffix}.json"
    with open(out_path, "w") as f:
        json.dump(enriched, f, indent=2, default=str)
    print(f"  Saved {count} devices to {out_path}")


def upload_to_supabase(enriched: list):
    """Upload enriched data to Supabase."""
    from supabase import create_client

    from config import SUPABASE_KEY, SUPABASE_URL

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  Supabase credentials not set, skipping upload")
        return

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    for device in enriched:
        # Upsert device
        device_row = {
            "fda_submission_number": device["fda_submission_number"],
            "device_name": device.get("device_name"),
            "company": device.get("company"),
            "decision_date": device.get("decision_date"),
            "specialty_panel": device.get("specialty_panel"),
            "product_code": device.get("product_code"),
            "evidence_score": device["score"]["total"],
            "evidence_count": device["score"]["detail"]["n_publications"],
            "safety_event_count": device["score"]["detail"]["n_safety_events"],
            "recall_count": device["score"]["detail"]["n_recalls"],
            "trial_count": device["score"]["detail"]["n_trials"],
        }
        result = (
            client.table("devices")
            .upsert(device_row, on_conflict="fda_submission_number")
            .execute()
        )
        device_id = result.data[0]["id"] if result.data else None

        if not device_id:
            continue

        # Upsert evidence
        for ev in device.get("evidence", []):
            client.table("evidence").upsert(
                {**ev, "device_id": device_id}, on_conflict="pmid"
            ).execute()

        # Upsert safety events
        for se in device.get("safety_events", []):
            if se.get("report_number"):
                client.table("safety_events").upsert(
                    {**se, "device_id": device_id}, on_conflict="report_number"
                ).execute()

        # Upsert recalls
        for rc in device.get("recalls", []):
            if rc.get("recall_number"):
                client.table("recalls").upsert(
                    {**rc, "device_id": device_id}, on_conflict="recall_number"
                ).execute()

        # Upsert trials
        for tr in device.get("trials", []):
            if tr.get("nct_id"):
                client.table("trials").upsert(
                    {**tr, "device_id": device_id}, on_conflict="nct_id"
                ).execute()

    print(f"  Uploaded {len(enriched)} devices to Supabase")


def _print_summary(enriched: list):
    total = len(enriched)
    detail_key = lambda d, k: d.get("score", {}).get("detail", {}).get(k, 0)
    zero_all = sum(1 for d in enriched if detail_key(d, "n_publications") == 0)
    zero_direct = sum(1 for d in enriched if detail_key(d, "n_direct_publications") == 0)
    has_events = sum(1 for d in enriched if detail_key(d, "n_safety_events") > 0)
    has_recalls = sum(1 for d in enriched if detail_key(d, "n_recalls") > 0)
    has_trials = sum(1 for d in enriched if detail_key(d, "n_trials") > 0)
    avg_score = sum(d["score"]["total"] for d in enriched) / total if total else 0

    from collections import Counter
    trusts = Counter(d.get("score", {}).get("trust_level", "none") for d in enriched)

    print("\n" + "=" * 60)
    print("ValidMed Pipeline Summary")
    print("=" * 60)
    print(f"Total devices:           {total}")
    print(f"Zero evidence (all):     {zero_all} ({zero_all/total*100:.0f}%)")
    print(f"Zero evidence (direct):  {zero_direct} ({zero_direct/total*100:.0f}%)")
    print(f"Has MAUDE events:        {has_events} ({has_events/total*100:.0f}%)")
    print(f"Has recalls:             {has_recalls} ({has_recalls/total*100:.0f}%)")
    print(f"Has clinical trials:     {has_trials} ({has_trials/total*100:.0f}%)")
    print(f"Average evidence score:  {avg_score:.1f}/100")
    print(f"Trust: strong={trusts.get('strong',0)} moderate={trusts.get('moderate',0)} limited={trusts.get('limited',0)} none={trusts.get('none',0)}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <path_to_fda_excel> [--limit N] [--upload] [--resume <checkpoint.json>]")
        sys.exit(1)

    excel_path = sys.argv[1]
    limit = None
    upload = False
    resume = None

    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
        if arg == "--upload":
            upload = True
        if arg == "--resume" and i + 1 < len(sys.argv):
            resume = sys.argv[i + 1]

    run_pipeline(excel_path, limit=limit, upload=upload, resume=resume)

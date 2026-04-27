"""Second-pass enrichment: adds 510(k) details and Semantic Scholar evidence.

Run AFTER the main pipeline completes:
  python enrich_pass2.py data/enriched_final.json
"""

import json
import sys
import time
from pathlib import Path

import enrich_510k
import enrich_semantic_scholar

DATA_DIR = Path(__file__).parent / "data"


def run_pass2(enriched_path: str):
    with open(enriched_path) as f:
        devices = json.load(f)

    total = len(devices)
    print(f"Pass 2: enriching {total} devices with 510(k) details + Semantic Scholar")

    # Phase 1: 510(k) details
    print("\n--- Phase 1: 510(k) clearance details ---")
    for i, device in enumerate(devices):
        k_number = device.get("fda_submission_number", "")
        if not k_number.startswith("K"):
            continue

        details = enrich_510k.fetch_510k_details(k_number)
        time.sleep(0.3)

        if details:
            device["clearance_details"] = details
            if details.get("device_class"):
                device["device_class"] = details["device_class"]

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{total}", flush=True)
            _save(devices, "pass2_510k")

    _save(devices, "pass2_510k")
    print(f"  Done. Added clearance details.")

    # Phase 2: Semantic Scholar
    print("\n--- Phase 2: Semantic Scholar (non-PubMed evidence) ---")
    new_evidence_count = 0
    for i, device in enumerate(devices):
        name = device.get("device_name", "")
        company = device.get("company", "")

        # Collect existing PMIDs to avoid duplicates
        existing_pmids = {e.get("pmid") for e in device.get("evidence", []) if e.get("pmid")}

        try:
            ss_results = enrich_semantic_scholar.enrich_device(name, company, existing_pmids)
        except Exception as e:
            print(f"  Error on {name}: {e}", flush=True)
            ss_results = []

        if ss_results:
            device.setdefault("evidence_semantic_scholar", []).extend(ss_results)
            new_evidence_count += len(ss_results)

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{total} ({new_evidence_count} new articles found)", flush=True)
            _save(devices, "pass2_full")

    _save(devices, "pass2_full")

    # Summary
    print("\n" + "=" * 60)
    print("Pass 2 Summary")
    print("=" * 60)

    has_class = sum(1 for d in devices if d.get("device_class"))
    has_summary = sum(1 for d in devices if d.get("clearance_details", {}).get("summary_url"))
    has_ss = sum(1 for d in devices if d.get("evidence_semantic_scholar"))

    # Recalculate zero-evidence including SS
    zero_all = sum(
        1 for d in devices
        if not d.get("evidence") and not d.get("evidence_semantic_scholar")
    )
    zero_pubmed_only = sum(1 for d in devices if not d.get("evidence"))

    print(f"Devices with device class: {has_class}/{total}")
    print(f"Devices with FDA summary PDF: {has_summary}/{total}")
    print(f"Devices with Semantic Scholar evidence: {has_ss}/{total}")
    print(f"Zero PubMed evidence: {zero_pubmed_only} ({zero_pubmed_only/total*100:.1f}%)")
    print(f"Zero ALL evidence (PubMed + SS): {zero_all} ({zero_all/total*100:.1f}%)")
    print(f"New articles from Semantic Scholar: {new_evidence_count}")
    print("=" * 60)

    # Save final
    out_path = DATA_DIR / "enriched_final_v2.json"
    with open(out_path, "w") as f:
        json.dump(devices, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


def _save(devices, label):
    out = DATA_DIR / f"enriched_{label}.json"
    with open(out, "w") as f:
        json.dump(devices, f, default=str)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enrich_pass2.py <enriched_final.json>")
        sys.exit(1)
    run_pass2(sys.argv[1])

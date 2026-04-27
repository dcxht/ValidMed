"""Pass 3: Multi-source evidence enrichment.

Runs AFTER the main pipeline (pass 1) completes. Adds:
1. Device alias-enhanced PubMed search
2. OpenAlex evidence (conferences, preprints, non-PubMed journals)
3. 510(k) summary PDF parsing (regulatory clinical data)
4. De Novo decision summary parsing
5. Predicate chain / product family evidence
6. 510(k) clearance details (device class, summary links)

Usage:
    python enrich_pass3.py data/enriched_final.json
"""

import json
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def run_pass3(input_path: str):
    print(f"Loading {input_path}...")
    with open(input_path) as f:
        devices = json.load(f)
    total = len(devices)
    print(f"  {total} devices loaded\n")

    # Phase 1: 510(k) clearance details (device class, summary links)
    print("=" * 60)
    print("Phase 1: 510(k) Clearance Details")
    print("=" * 60)
    import enrich_510k
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
    _save(devices, "pass3_phase1")
    print("  Done.\n")

    # Phase 2: Predicate chain / product family evidence
    print("=" * 60)
    print("Phase 2: Product Family Evidence")
    print("=" * 60)
    import predicate_chains
    devices = predicate_chains.enrich_with_family_evidence(devices)
    _save(devices, "pass3_phase2")
    has_family = sum(1 for d in devices if d.get("family_evidence", {}).get("family_has_evidence"))
    print(f"  {has_family} devices gained family evidence.\n")

    # Phase 3: De Novo decision summaries
    print("=" * 60)
    print("Phase 3: De Novo Decision Summaries")
    print("=" * 60)
    import enrich_denovo
    devices = enrich_denovo.enrich_denovo_devices(devices)
    _save(devices, "pass3_phase3")
    print()

    # Phase 4: OpenAlex evidence
    print("=" * 60)
    print("Phase 4: OpenAlex Evidence (conferences, preprints)")
    print("=" * 60)
    import enrich_openalex
    new_openalex = 0
    for i, device in enumerate(devices):
        name = device.get("device_name", "")
        company = device.get("company", "")

        # Collect existing PMIDs to avoid duplicates
        existing_pmids = set()
        for e in device.get("evidence", []):
            if e.get("pmid"):
                existing_pmids.add(e["pmid"])

        try:
            oa_results = enrich_openalex.enrich_device(name, company, existing_pmids)
        except Exception as e:
            oa_results = []

        if oa_results:
            device.setdefault("evidence_openalex", []).extend(oa_results)
            new_openalex += len(oa_results)

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{total} ({new_openalex} new articles)", flush=True)
            _save(devices, "pass3_phase4")

    _save(devices, "pass3_phase4")
    print(f"  {new_openalex} new articles from OpenAlex.\n")

    # Phase 5: 510(k) summary PDF parsing (regulatory clinical data)
    # This downloads PDFs — only run for devices with no other evidence
    print("=" * 60)
    print("Phase 5: 510(k) Summary PDFs (devices with no evidence)")
    print("=" * 60)
    import enrich_510k_summaries
    parsed_count = 0
    for i, device in enumerate(devices):
        k_number = device.get("fda_submission_number", "")
        if not k_number.startswith("K"):
            continue

        # Only parse PDFs for devices with limited or no evidence
        n_direct = device.get("score", {}).get("detail", {}).get("n_direct_publications", 0)
        n_openalex = len(device.get("evidence_openalex", []))
        if n_direct > 0 or n_openalex > 0:
            continue  # Already has published evidence

        try:
            result = enrich_510k_summaries.parse_510k_summary(k_number)
            if result and result.get("has_clinical_data"):
                device["regulatory_evidence"] = result
                parsed_count += 1
        except Exception:
            pass

        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{total} ({parsed_count} with clinical data)", flush=True)

    _save(devices, "pass3_phase5")
    print(f"  {parsed_count} devices gained regulatory clinical data.\n")

    # Final save
    out_path = DATA_DIR / "enriched_final_v3.json"
    with open(out_path, "w") as f:
        json.dump(devices, f, indent=2, default=str)
    print(f"Saved to {out_path}")

    # Summary
    _print_summary(devices)


def _save(devices, label):
    out = DATA_DIR / f"enriched_{label}.json"
    with open(out, "w") as f:
        json.dump(devices, f, default=str)


def _print_summary(devices):
    total = len(devices)
    detail = lambda d, k: d.get("score", {}).get("detail", {}).get(k, 0)

    zero_pubmed = sum(1 for d in devices if detail(d, "n_publications") == 0)
    zero_direct = sum(1 for d in devices if detail(d, "n_direct_publications") == 0)
    has_openalex = sum(1 for d in devices if d.get("evidence_openalex"))
    has_regulatory = sum(1 for d in devices if d.get("regulatory_evidence", {}).get("has_clinical_data"))
    has_family = sum(1 for d in devices if d.get("family_evidence", {}).get("family_has_evidence"))
    has_denovo = sum(1 for d in devices if d.get("denovo_summary"))
    has_device_class = sum(1 for d in devices if d.get("device_class"))

    # True zero = no evidence from ANY source
    true_zero = sum(
        1 for d in devices
        if detail(d, "n_publications") == 0
        and not d.get("evidence_openalex")
        and not d.get("regulatory_evidence", {}).get("has_clinical_data")
        and not d.get("family_evidence", {}).get("family_has_evidence")
    )

    print("\n" + "=" * 60)
    print("ValidMed Pass 3 — Multi-Source Evidence Summary")
    print("=" * 60)
    print(f"Total devices:                 {total}")
    print(f"Zero PubMed evidence:          {zero_pubmed} ({zero_pubmed/total*100:.0f}%)")
    print(f"Zero direct PubMed evidence:   {zero_direct} ({zero_direct/total*100:.0f}%)")
    print(f"Has OpenAlex evidence:         {has_openalex} ({has_openalex/total*100:.0f}%)")
    print(f"Has regulatory clinical data:  {has_regulatory} ({has_regulatory/total*100:.0f}%)")
    print(f"Has product family evidence:   {has_family} ({has_family/total*100:.0f}%)")
    print(f"Has De Novo summary:           {has_denovo}")
    print(f"Has device class:              {has_device_class}")
    print(f"")
    print(f"TRUE ZERO (no evidence from any source): {true_zero} ({true_zero/total*100:.0f}%)")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enrich_pass3.py <enriched_final.json>")
        sys.exit(1)
    run_pass3(sys.argv[1])

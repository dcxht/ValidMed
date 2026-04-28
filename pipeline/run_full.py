"""ValidMed Full Pipeline Orchestrator

Runs ALL evidence sources sequentially on one clean dataset.
Produces a single authoritative enriched_final.json with data from:
  1. PubMed (multi-tier search with aliases)
  2. openFDA MAUDE (adverse events)
  3. openFDA Recalls
  4. OpenAlex (conferences, preprints, non-PubMed journals)
  5. ClinicalTrials.gov (if accessible)
  6. 510(k) clearance details (device class, summary links)
  7. Predicate chain / product family evidence
  8. LLM relevance validation (Claude Haiku with abstracts)
  9. Study type reclassification
  10. Score computation + trust levels
  11. Export to dashboard

Usage:
    cd ~/MedRADAR/pipeline && source .venv/bin/activate
    python run_full.py "data/ai-ml-enabled-devices-excel (1).xlsx"

    # Resume from a specific step (if a step fails):
    python run_full.py "data/ai-ml-enabled-devices-excel (1).xlsx" --resume-from 4

    # Skip ClinicalTrials.gov (if 403 errors):
    python run_full.py "data/ai-ml-enabled-devices-excel (1).xlsx" --skip-ctgov

Estimated time: 2-3 hours total
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
LOG_FILE = Path(__file__).parent / "run_full.log"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def save(devices: list, label: str):
    path = DATA_DIR / f"enriched_{label}.json"
    with open(path, "w") as f:
        json.dump(devices, f, indent=2, default=str)
    log(f"  Saved {len(devices)} devices to {path}")
    return path


def step1_pubmed(excel_path: str) -> list:
    """Parse FDA list + PubMed multi-tier search with aliases."""
    log("STEP 1: Parse FDA device list + PubMed search")
    from parse_fda_list import parse_fda_excel
    import enrich_pubmed
    import enrich_openfda
    import score

    devices = parse_fda_excel(excel_path)
    log(f"  {len(devices)} devices parsed")

    enriched = []
    for i, device in enumerate(devices):
        name = device.get("device_name", "")
        company = device.get("company", "")
        k_number = device.get("fda_submission_number", "")
        specialty = device.get("specialty_panel", "")

        if (i + 1) % 50 == 0 or i == 0:
            log(f"  [{i+1}/{len(devices)}] {name[:40]}")

        evidence = []
        fda_data = {"safety_events": [], "recalls": []}

        for attempt in range(3):
            try:
                evidence = enrich_pubmed.enrich_device(name, company, specialty)
                fda_data = enrich_openfda.enrich_device(k_number, name, company)
                break
            except Exception as e:
                log(f"    Retry {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)

        device_score = score.compute_score(
            evidence, fda_data["safety_events"], fda_data["recalls"], []
        )

        enriched.append({
            **device,
            "evidence": evidence,
            "safety_events": fda_data["safety_events"],
            "recalls": fda_data["recalls"],
            "trials": [],
            "score": device_score,
        })

        if (i + 1) % 100 == 0:
            save(enriched, f"step1_checkpoint_{i+1}")

    save(enriched, "step1_pubmed")
    n_with_ev = sum(1 for d in enriched if d["score"]["detail"]["n_publications"] > 0)
    log(f"  PubMed complete: {n_with_ev}/{len(enriched)} have evidence")
    return enriched


def step2_openalex(devices: list) -> list:
    """Add OpenAlex evidence (conferences, preprints, non-PubMed)."""
    log("STEP 2: OpenAlex evidence search")
    import enrich_openalex

    new_count = 0
    for i, device in enumerate(devices):
        name = device.get("device_name", "")
        company = device.get("company", "")

        existing_pmids = {e.get("pmid") for e in device.get("evidence", []) if e.get("pmid")}

        try:
            oa_results = enrich_openalex.enrich_device(name, company, existing_pmids)
        except Exception:
            oa_results = []

        if oa_results:
            device["evidence_openalex"] = oa_results
            new_count += len(oa_results)

        if (i + 1) % 200 == 0:
            log(f"  [{i+1}/{len(devices)}] ({new_count} new articles)")

    save(devices, "step2_openalex")
    log(f"  OpenAlex complete: {new_count} new articles found")
    return devices


def step3_ctgov(devices: list) -> list:
    """Add ClinicalTrials.gov data."""
    log("STEP 3: ClinicalTrials.gov")
    import enrich_trials

    trial_count = 0
    for i, device in enumerate(devices):
        name = device.get("device_name", "")
        company = device.get("company", "")

        try:
            trials = enrich_trials.enrich_device(name, company)
            # Filter out manual followup entries
            trials = [t for t in trials if not t.get("_manual_followup")]
            if trials:
                device["trials"] = trials
                trial_count += len(trials)
        except Exception:
            pass

        if (i + 1) % 200 == 0:
            log(f"  [{i+1}/{len(devices)}] ({trial_count} trials found)")

    save(devices, "step3_ctgov")
    log(f"  ClinicalTrials.gov complete: {trial_count} trials found")
    return devices


def step4_510k_details(devices: list) -> list:
    """Add 510(k) clearance details (device class, summary links)."""
    log("STEP 4: 510(k) clearance details")
    import enrich_510k

    enriched_count = 0
    for i, device in enumerate(devices):
        k_number = device.get("fda_submission_number", "")
        if not k_number.startswith("K"):
            continue

        try:
            details = enrich_510k.fetch_510k_details(k_number)
            time.sleep(0.3)
            if details:
                device["clearance_details"] = details
                if details.get("device_class"):
                    device["device_class"] = details["device_class"]
                enriched_count += 1
        except Exception:
            pass

        if (i + 1) % 200 == 0:
            log(f"  [{i+1}/{len(devices)}] ({enriched_count} enriched)")

    save(devices, "step4_510k")
    log(f"  510(k) details complete: {enriched_count} devices enriched")
    return devices


def step5_families(devices: list) -> list:
    """Add predicate chain / product family evidence."""
    log("STEP 5: Product family evidence")
    import predicate_chains

    devices = predicate_chains.enrich_with_family_evidence(devices)

    gained = sum(
        1 for d in devices
        if d.get("family_evidence", {}).get("inherited_publication_count", 0) > 0
    )
    save(devices, "step5_families")
    log(f"  Family evidence complete: {gained} devices gained family evidence")
    return devices


def step6_llm_validation(devices: list) -> list:
    """LLM relevance validation with abstracts."""
    log("STEP 6: LLM relevance validation")

    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        log("  WARNING: No ANTHROPIC_API_KEY set. Skipping LLM validation.")
        save(devices, "step6_validated")
        return devices

    from validate_relevance import validate_with_llm
    from score import compute_score

    total_reviewed = 0
    total_removed = 0

    for i, device in enumerate(devices):
        evidence = device.get("evidence", [])
        direct = [e for e in evidence if e.get("match_tier") == "direct"]

        if not direct:
            continue

        name = device.get("device_name", "")
        company = device.get("company", "")
        specialty = device.get("specialty_panel", "")

        validated = validate_with_llm(name, company, specialty, direct)
        company_evidence = [e for e in evidence if e.get("match_tier") != "direct"]
        device["evidence"] = validated + company_evidence

        irrelevant = sum(1 for a in validated if a.get("relevance") == "irrelevant")
        total_removed += irrelevant
        total_reviewed += len(direct)

        # Recompute score
        cleaned = [e for e in device["evidence"] if e.get("relevance") != "irrelevant"]
        device["evidence"] = cleaned
        device["score"] = compute_score(
            cleaned,
            device.get("safety_events", []),
            device.get("recalls", []),
            device.get("trials", []),
        )

        if (i + 1) % 100 == 0:
            log(f"  [{i+1}/{len(devices)}] reviewed={total_reviewed}, removed={total_removed}")
            save(devices, "step6_checkpoint")

    save(devices, "step6_validated")
    log(f"  LLM validation complete: {total_reviewed} reviewed, {total_removed} removed")
    return devices


def step7_reclassify(devices: list) -> list:
    """Reclassify study types using title keyword fallback."""
    log("STEP 7: Study type reclassification")
    from reclassify_study_types import classify
    from score import compute_score

    changed = 0
    for device in devices:
        for article in device.get("evidence", []):
            old = article.get("study_type", "other")
            new = classify(article)
            if old != new:
                article["study_type"] = new
                changed += 1

        device["score"] = compute_score(
            device.get("evidence", []),
            device.get("safety_events", []),
            device.get("recalls", []),
            device.get("trials", []),
        )

    save(devices, "step7_reclassified")
    log(f"  Reclassification complete: {changed} articles reclassified")
    return devices


def step8_export(devices: list) -> list:
    """Export to dashboard and generate analysis outputs."""
    log("STEP 8: Final export + analysis")

    # Save final
    final_path = save(devices, "final")

    # Export to dashboard
    from export_static import export_static
    export_static(str(final_path))

    # Generate figures
    try:
        from generate_figures import generate_all
        generate_all(str(final_path))
    except Exception as e:
        log(f"  Figure generation failed: {e}")

    # PRISMA flow
    try:
        from prisma_flow import analyze_flow
        analyze_flow(str(final_path))
    except Exception as e:
        log(f"  PRISMA flow failed: {e}")

    # Sensitivity analysis
    try:
        from sensitivity_analysis import run_analysis
        run_analysis(str(final_path))
    except Exception as e:
        log(f"  Sensitivity analysis failed: {e}")

    # Final summary
    from collections import Counter
    total = len(devices)
    trusts = Counter(d.get("score", {}).get("trust_level", "none") for d in devices)
    zero_ev = sum(1 for d in devices if d.get("score", {}).get("detail", {}).get("n_publications", 0) == 0)
    has_oa = sum(1 for d in devices if d.get("evidence_openalex"))
    has_trials = sum(1 for d in devices if d.get("trials"))
    has_family = sum(1 for d in devices if d.get("family_evidence", {}).get("inherited_publication_count", 0) > 0)

    log("")
    log("=" * 60)
    log("VALIDMED FINAL RESULTS")
    log("=" * 60)
    log(f"Total devices:           {total}")
    log(f"Zero PubMed evidence:    {zero_ev} ({zero_ev/total*100:.1f}%)")
    log(f"Has OpenAlex evidence:   {has_oa}")
    log(f"Has clinical trials:     {has_trials}")
    log(f"Has family evidence:     {has_family}")
    log(f"Trust levels:")
    for level in ["strong", "moderate", "limited", "none"]:
        n = trusts.get(level, 0)
        log(f"  {level}: {n} ({n/total*100:.1f}%)")
    log(f"Dataset frozen at:       {datetime.now().isoformat()}")
    log("=" * 60)

    return devices


STEPS = {
    1: ("PubMed + MAUDE + Recalls", step1_pubmed),
    2: ("OpenAlex", step2_openalex),
    3: ("ClinicalTrials.gov", step3_ctgov),
    4: ("510(k) details", step4_510k_details),
    5: ("Product family evidence", step5_families),
    6: ("LLM relevance validation", step6_llm_validation),
    7: ("Study type reclassification", step7_reclassify),
    8: ("Export + analysis", step8_export),
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_full.py <fda_excel> [--resume-from N] [--skip-ctgov]")
        sys.exit(1)

    excel_path = sys.argv[1]
    resume_from = 1
    skip_ctgov = "--skip-ctgov" in sys.argv

    for i, arg in enumerate(sys.argv):
        if arg == "--resume-from" and i + 1 < len(sys.argv):
            resume_from = int(sys.argv[i + 1])

    # Clear log
    if resume_from == 1:
        LOG_FILE.write_text("")

    log(f"ValidMed Full Pipeline - started {datetime.now().isoformat()}")
    log(f"FDA Excel: {excel_path}")
    log(f"Resume from step: {resume_from}")
    log(f"Skip ClinicalTrials.gov: {skip_ctgov}")
    log("")

    DATA_DIR.mkdir(exist_ok=True)
    devices = None

    for step_num in sorted(STEPS.keys()):
        step_name, step_fn = STEPS[step_num]

        if step_num < resume_from:
            log(f"STEP {step_num}: {step_name} - SKIPPED (resuming)")
            # Load previous step's output
            prev_file = DATA_DIR / f"enriched_step{step_num}_*.json"
            import glob
            matches = sorted(glob.glob(str(DATA_DIR / f"enriched_step{step_num}*.json")))
            if matches:
                with open(matches[-1]) as f:
                    devices = json.load(f)
                log(f"  Loaded {len(devices)} devices from {matches[-1]}")
            continue

        if step_num == 3 and skip_ctgov:
            log(f"STEP {step_num}: {step_name} - SKIPPED (--skip-ctgov)")
            continue

        log("")
        start = time.time()

        try:
            if step_num == 1:
                devices = step_fn(excel_path)
            else:
                if devices is None:
                    # Try to load from previous step
                    prev = DATA_DIR / f"enriched_step{step_num-1}*.json"
                    import glob
                    matches = sorted(glob.glob(str(DATA_DIR / f"enriched_step{step_num-1}*.json")))
                    if not matches:
                        matches = sorted(glob.glob(str(DATA_DIR / "enriched_final.json")))
                    if matches:
                        with open(matches[-1]) as f:
                            devices = json.load(f)
                        log(f"  Loaded {len(devices)} devices from {matches[-1]}")
                    else:
                        log(f"  ERROR: No data found for step {step_num}. Run from step 1.")
                        sys.exit(1)

                devices = step_fn(devices)

        except Exception as e:
            log(f"  STEP {step_num} FAILED: {e}")
            log(f"  Resume with: python run_full.py \"{excel_path}\" --resume-from {step_num}")
            import traceback
            log(traceback.format_exc())
            sys.exit(1)

        elapsed = time.time() - start
        log(f"  Step {step_num} completed in {elapsed/60:.1f} minutes")

    log(f"\nFull pipeline completed at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()

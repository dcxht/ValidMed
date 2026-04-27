"""Baseline comparison: non-AI 510(k) devices vs AI devices.

Addresses the critique: "Maybe all 510(k) devices lack published evidence,
not just AI ones." Samples ~200 non-AI devices from the same specialties
and time period as the AI devices, runs the same PubMed evidence search,
and computes comparison statistics.

Usage:
    python baseline_comparison.py [--sample-size 200] [--dry-run]
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

# Add pipeline dir to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))

from config import OPENFDA_API_KEY, OPENFDA_DELAY
from enrich_pubmed import enrich_device

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENFDA_510K_URL = "https://api.fda.gov/device/510k.json"

# Known AI/ML product codes to EXCLUDE from baseline
AI_PRODUCT_CODES = {"QAS", "QBS", "QMT", "QDQ", "QIH", "LLZ", "POK", "MYN"}

# Advisory committee codes mapped to specialty names
# https://www.fda.gov/medical-devices/classify-your-medical-device/device-classification-panels
SPECIALTY_MAP = {
    "RA": "Radiology",
    "CV": "Cardiovascular",
    "NE": "Neurology",
}

# Target sample per specialty (will be split roughly evenly)
DEFAULT_SAMPLE_SIZE = 200

# Date range matching the AI device dataset
DATE_START = "20200101"
DATE_END = "20251231"

OUTPUT_PATH = Path(__file__).parent / "data" / "baseline_comparison.json"


# ---------------------------------------------------------------------------
# openFDA fetching with retry
# ---------------------------------------------------------------------------

def fetch_510k_devices(advisory_committee: str, limit: int = 100, skip: int = 0) -> list[dict]:
    """Fetch non-AI 510(k) devices from openFDA for a given advisory committee.

    Excludes known AI product codes. Returns raw openFDA result dicts.
    """
    # Build product code exclusion filter
    exclusions = " AND ".join(f'product_code:"{code}"' for code in AI_PRODUCT_CODES)
    search = (
        f'advisory_committee:"{advisory_committee}"'
        f" AND decision_date:[{DATE_START} TO {DATE_END}]"
        f" AND NOT ({exclusions})"
    )

    params = {
        "search": search,
        "limit": limit,
        "skip": skip,
    }
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY

    for attempt in range(4):
        try:
            resp = httpx.get(OPENFDA_510K_URL, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  [rate limited] waiting {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                # No results
                return []
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except httpx.HTTPStatusError as e:
            print(f"  [HTTP {e.response.status_code}] retry {attempt + 1}/4")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"  [error: {e}] retry {attempt + 1}/4")
            time.sleep(2 ** attempt)

    return []


def sample_non_ai_devices(per_specialty: int = 67) -> list[dict]:
    """Sample non-AI devices from each specialty panel.

    Fetches a larger batch and randomly samples to avoid bias from
    the openFDA default ordering.
    """
    all_devices = []

    for code, specialty in SPECIALTY_MAP.items():
        print(f"\nFetching {specialty} (advisory_committee={code})...")

        # Fetch up to 300 results to sample from (openFDA max skip+limit=5000)
        # Use a random skip offset to get varied devices
        max_available = 1000  # conservative estimate
        skip = random.randint(0, min(max_available - 100, 500))

        batch = fetch_510k_devices(code, limit=100, skip=skip)
        time.sleep(OPENFDA_DELAY)

        if len(batch) < per_specialty:
            # Try another offset
            skip2 = random.randint(0, 200)
            batch2 = fetch_510k_devices(code, limit=100, skip=skip2)
            time.sleep(OPENFDA_DELAY)
            # Deduplicate by k_number
            seen = {d.get("k_number") for d in batch}
            for d in batch2:
                if d.get("k_number") not in seen:
                    batch.append(d)
                    seen.add(d.get("k_number"))

        # Random sample
        if len(batch) > per_specialty:
            batch = random.sample(batch, per_specialty)

        for device in batch:
            all_devices.append({
                "k_number": device.get("k_number", ""),
                "device_name": device.get("device_name", ""),
                "applicant": device.get("applicant", ""),
                "decision_date": device.get("decision_date", ""),
                "product_code": device.get("product_code", ""),
                "advisory_committee": code,
                "specialty": specialty,
            })

        print(f"  Sampled {len(batch)} devices from {specialty}")

    return all_devices


# ---------------------------------------------------------------------------
# PubMed enrichment with throttling
# ---------------------------------------------------------------------------

def enrich_devices_with_evidence(devices: list[dict]) -> list[dict]:
    """Run PubMed evidence search on each device (same as AI pipeline)."""
    total = len(devices)
    for i, device in enumerate(devices):
        print(f"  [{i+1}/{total}] {device['device_name'][:50]}...", end=" ")

        try:
            evidence = enrich_device(
                device["device_name"],
                device["applicant"],
                device["specialty"],
            )
            device["evidence"] = evidence
            device["evidence_count"] = len(evidence)
            print(f"-> {len(evidence)} articles")
        except Exception as e:
            print(f"-> ERROR: {e}")
            device["evidence"] = []
            device["evidence_count"] = 0

        # Extra throttle to be kind to PubMed
        time.sleep(0.5)

        # Checkpoint every 50 devices
        if (i + 1) % 50 == 0:
            print(f"  ... checkpoint at {i+1}/{total}")

    return devices


# ---------------------------------------------------------------------------
# Comparison statistics
# ---------------------------------------------------------------------------

def load_ai_device_stats() -> dict:
    """Load AI device evidence stats from the enriched checkpoints."""
    data_dir = Path(__file__).parent / "data"
    ai_devices = []

    # Load all checkpoint files
    for f in sorted(data_dir.glob("enriched_checkpoint_*.json")):
        with open(f) as fh:
            ai_devices.extend(json.load(fh))

    if not ai_devices:
        print("WARNING: No AI device data found in enriched_checkpoint_*.json files.")
        return {
            "total_devices": 0,
            "devices_with_evidence": 0,
            "evidence_rate": 0.0,
            "mean_articles_per_device": 0.0,
            "mean_articles_when_found": 0.0,
            "by_specialty": {},
        }

    # Deduplicate by submission number
    seen = set()
    unique = []
    for d in ai_devices:
        key = d.get("fda_submission_number", d.get("k_number", ""))
        if key not in seen:
            seen.add(key)
            unique.append(d)

    total = len(unique)
    with_evidence = sum(1 for d in unique if len(d.get("evidence", [])) > 0)
    all_counts = [len(d.get("evidence", [])) for d in unique]
    nonzero_counts = [c for c in all_counts if c > 0]

    by_specialty = {}
    for d in unique:
        spec = d.get("specialty_panel", "Unknown")
        if spec not in by_specialty:
            by_specialty[spec] = {"total": 0, "with_evidence": 0, "article_counts": []}
        by_specialty[spec]["total"] += 1
        n = len(d.get("evidence", []))
        by_specialty[spec]["article_counts"].append(n)
        if n > 0:
            by_specialty[spec]["with_evidence"] += 1

    for spec, stats in by_specialty.items():
        stats["evidence_rate"] = stats["with_evidence"] / stats["total"] if stats["total"] > 0 else 0
        stats["mean_articles"] = sum(stats["article_counts"]) / len(stats["article_counts"]) if stats["article_counts"] else 0
        del stats["article_counts"]  # Don't need in output

    return {
        "total_devices": total,
        "devices_with_evidence": with_evidence,
        "evidence_rate": with_evidence / total if total > 0 else 0,
        "mean_articles_per_device": sum(all_counts) / total if total > 0 else 0,
        "mean_articles_when_found": sum(nonzero_counts) / len(nonzero_counts) if nonzero_counts else 0,
        "by_specialty": by_specialty,
    }


def compute_baseline_stats(devices: list[dict]) -> dict:
    """Compute evidence statistics for the non-AI baseline devices."""
    total = len(devices)
    with_evidence = sum(1 for d in devices if d.get("evidence_count", 0) > 0)
    all_counts = [d.get("evidence_count", 0) for d in devices]
    nonzero_counts = [c for c in all_counts if c > 0]

    by_specialty = {}
    for d in devices:
        spec = d.get("specialty", "Unknown")
        if spec not in by_specialty:
            by_specialty[spec] = {"total": 0, "with_evidence": 0, "article_counts": []}
        by_specialty[spec]["total"] += 1
        n = d.get("evidence_count", 0)
        by_specialty[spec]["article_counts"].append(n)
        if n > 0:
            by_specialty[spec]["with_evidence"] += 1

    for spec, stats in by_specialty.items():
        stats["evidence_rate"] = stats["with_evidence"] / stats["total"] if stats["total"] > 0 else 0
        stats["mean_articles"] = sum(stats["article_counts"]) / len(stats["article_counts"]) if stats["article_counts"] else 0
        del stats["article_counts"]

    return {
        "total_devices": total,
        "devices_with_evidence": with_evidence,
        "evidence_rate": with_evidence / total if total > 0 else 0,
        "mean_articles_per_device": sum(all_counts) / total if total > 0 else 0,
        "mean_articles_when_found": sum(nonzero_counts) / len(nonzero_counts) if nonzero_counts else 0,
        "by_specialty": by_specialty,
    }


def print_comparison(ai_stats: dict, baseline_stats: dict):
    """Print a formatted comparison summary."""
    print("\n" + "=" * 70)
    print("COMPARISON: AI/ML Devices vs Non-AI 510(k) Devices")
    print("=" * 70)
    print(f"{'Metric':<40} {'AI Devices':>14} {'Non-AI':>14}")
    print("-" * 70)
    print(f"{'Total devices sampled':<40} {ai_stats['total_devices']:>14} {baseline_stats['total_devices']:>14}")
    print(f"{'Devices with any evidence':<40} {ai_stats['devices_with_evidence']:>14} {baseline_stats['devices_with_evidence']:>14}")
    print(f"{'Evidence rate':<40} {ai_stats['evidence_rate']:>13.1%} {baseline_stats['evidence_rate']:>13.1%}")
    print(f"{'Mean articles per device':<40} {ai_stats['mean_articles_per_device']:>14.2f} {baseline_stats['mean_articles_per_device']:>14.2f}")
    print(f"{'Mean articles (when found)':<40} {ai_stats['mean_articles_when_found']:>14.2f} {baseline_stats['mean_articles_when_found']:>14.2f}")

    print("\n--- By Specialty ---")
    all_specs = set(list(ai_stats.get("by_specialty", {}).keys()) +
                    list(baseline_stats.get("by_specialty", {}).keys()))
    for spec in sorted(all_specs):
        ai_s = ai_stats.get("by_specialty", {}).get(spec, {})
        bl_s = baseline_stats.get("by_specialty", {}).get(spec, {})
        ai_rate = ai_s.get("evidence_rate", 0)
        bl_rate = bl_s.get("evidence_rate", 0)
        ai_n = ai_s.get("total", 0)
        bl_n = bl_s.get("total", 0)
        print(f"  {spec:<20} AI: {ai_rate:.1%} (n={ai_n:>3})   Non-AI: {bl_rate:.1%} (n={bl_n:>3})")

    print("\n" + "=" * 70)
    diff = ai_stats["evidence_rate"] - baseline_stats["evidence_rate"]
    if diff > 0.05:
        print(f"FINDING: AI devices have HIGHER evidence rate (+{diff:.1%})")
    elif diff < -0.05:
        print(f"FINDING: AI devices have LOWER evidence rate ({diff:.1%})")
    else:
        print(f"FINDING: Evidence rates are SIMILAR (delta: {diff:+.1%})")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compare AI vs non-AI 510(k) device evidence")
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE,
                        help="Total number of non-AI devices to sample (default: 200)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only fetch devices from openFDA, skip PubMed enrichment")
    args = parser.parse_args()

    per_specialty = args.sample_size // len(SPECIALTY_MAP)
    print(f"Sampling ~{args.sample_size} non-AI 510(k) devices "
          f"({per_specialty} per specialty) cleared 2020-2025...")

    # Step 1: Sample non-AI devices from openFDA
    devices = sample_non_ai_devices(per_specialty=per_specialty)
    print(f"\nTotal non-AI devices sampled: {len(devices)}")

    if not devices:
        print("ERROR: No devices fetched from openFDA. Check API key / network.")
        sys.exit(1)

    # Step 2: Run PubMed evidence search (unless dry-run)
    if not args.dry_run:
        print("\nRunning PubMed evidence search on non-AI devices...")
        devices = enrich_devices_with_evidence(devices)
    else:
        print("\n[DRY RUN] Skipping PubMed enrichment.")
        for d in devices:
            d["evidence"] = []
            d["evidence_count"] = 0

    # Step 3: Compute statistics
    baseline_stats = compute_baseline_stats(devices)
    ai_stats = load_ai_device_stats()

    # Step 4: Print comparison
    print_comparison(ai_stats, baseline_stats)

    # Step 5: Save results
    output = {
        "generated_at": datetime.now().isoformat(),
        "methodology": {
            "description": "Sampled non-AI 510(k) devices from same specialties and time period as AI devices",
            "specialties": list(SPECIALTY_MAP.values()),
            "date_range": f"{DATE_START}-{DATE_END}",
            "excluded_product_codes": sorted(AI_PRODUCT_CODES),
            "pubmed_search_method": "Same enrich_pubmed.enrich_device() function used for AI devices",
        },
        "ai_devices": ai_stats,
        "non_ai_baseline": baseline_stats,
        "comparison": {
            "evidence_rate_difference": ai_stats["evidence_rate"] - baseline_stats["evidence_rate"],
            "interpretation": (
                "Positive = AI devices have more evidence; "
                "Negative = non-AI devices have more evidence"
            ),
        },
        "non_ai_device_details": devices,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

"""Trace 510(k) predicate device chains via product_code family grouping.

When Device B cites Device A as its predicate in a 510(k) submission, the FDA
has determined substantial equivalence. Devices sharing the same FDA product
code are regulatory siblings -- cleared for the same intended use through the
same classification. If any device in the family has published evidence, that
evidence is indirectly relevant to all family members.

This module groups devices by product_code, identifies which devices have
direct PubMed evidence, and tags evidence-poor devices with "family_evidence"
inherited from their product_code siblings.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import httpx

from config import OPENFDA_API_KEY, OPENFDA_BASE, OPENFDA_DELAY

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_params(search: str, limit: int = 100) -> dict:
    params = {"search": search, "limit": limit}
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY
    return params


def _count_direct_evidence(device: dict) -> int:
    """Count publications with a 'direct' match tier."""
    return sum(
        1 for pub in device.get("evidence", [])
        if pub.get("match_tier") == "direct"
    )


def _count_all_evidence(device: dict) -> int:
    """Count all publications regardless of match tier."""
    return len(device.get("evidence", []))


# ---------------------------------------------------------------------------
# openFDA 510(k) family lookup
# ---------------------------------------------------------------------------


def fetch_family_members(product_code: str) -> list[dict]:
    """Query openFDA device/510k for all clearances sharing a product_code.

    Returns a list of dicts with k_number, device_name, applicant, and
    decision_date for each cleared device in the family.
    """
    search = f'product_code:"{product_code}"'
    params = _build_params(search, limit=100)

    try:
        resp = httpx.get(
            f"{OPENFDA_BASE}/device/510k.json", params=params, timeout=30
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        return []

    data = resp.json()
    results = []
    seen = set()

    for entry in data.get("results", []):
        k_num = entry.get("k_number", "")
        if not k_num or k_num in seen:
            continue
        seen.add(k_num)
        results.append({
            "k_number": k_num,
            "device_name": entry.get("device_name", ""),
            "applicant": entry.get("applicant", ""),
            "decision_date": entry.get("decision_date", ""),
            "product_code": product_code,
        })

    return results


# ---------------------------------------------------------------------------
# Family graph construction
# ---------------------------------------------------------------------------


def build_family_graph(devices: list[dict]) -> dict:
    """Group devices by product_code into device families.

    Returns a dict mapping each product_code to a family record::

        {
            "QIH": {
                "product_code": "QIH",
                "members": [
                    {"k_number": "K253532", "device_name": "...", ...},
                    ...
                ],
                "members_with_evidence": [
                    {"k_number": "K253532", "device_name": "...",
                     "n_direct": 0, "n_total": 3},
                ],
                "family_size": 5,
                "family_evidence_count": 3,
            },
            ...
        }
    """
    # Step 1: group our devices by product_code
    code_groups: dict[str, list[dict]] = defaultdict(list)
    for dev in devices:
        pc = dev.get("product_code", "")
        if pc:
            code_groups[pc].append(dev)

    graph: dict[str, dict] = {}

    for product_code, group in code_groups.items():
        members = []
        members_with_evidence = []

        for dev in group:
            member_info = {
                "k_number": dev.get("fda_submission_number", ""),
                "device_name": dev.get("device_name", ""),
                "company": dev.get("company", ""),
            }
            members.append(member_info)

            n_direct = _count_direct_evidence(dev)
            n_total = _count_all_evidence(dev)

            if n_total > 0:
                members_with_evidence.append({
                    **member_info,
                    "n_direct": n_direct,
                    "n_total": n_total,
                })

        total_family_pubs = sum(
            _count_all_evidence(d) for d in group
        )

        graph[product_code] = {
            "product_code": product_code,
            "members": members,
            "members_with_evidence": members_with_evidence,
            "family_size": len(members),
            "family_evidence_count": total_family_pubs,
        }

    return graph


def expand_families_from_openfda(
    graph: dict, delay: float = OPENFDA_DELAY
) -> dict:
    """Optionally expand each family with additional 510(k) clearances from
    openFDA that are NOT in our local device list.

    This enriches the graph with the broader regulatory family -- other
    devices cleared under the same product code that may not be in our
    dataset but share regulatory lineage.

    Mutates and returns the graph dict.
    """
    for product_code, family in graph.items():
        local_k_numbers = {m["k_number"] for m in family["members"]}

        fda_members = fetch_family_members(product_code)
        time.sleep(delay)

        external_members = [
            m for m in fda_members if m["k_number"] not in local_k_numbers
        ]

        family["fda_family_members"] = external_members
        family["fda_family_size"] = len(fda_members)

        if external_members:
            print(
                f"  {product_code}: {len(external_members)} additional "
                f"510(k)s found on openFDA "
                f"(total family: {len(fda_members)})"
            )

    return graph


# ---------------------------------------------------------------------------
# Enrichment: tag devices with inherited family evidence
# ---------------------------------------------------------------------------


def enrich_with_family_evidence(
    devices: list[dict],
    expand_from_openfda: bool = False,
) -> list[dict]:
    """Tag each device with evidence inherited from its product_code family.

    For devices that have zero direct publications, this finds other devices
    in the same product_code family that DO have evidence, and attaches a
    ``family_evidence`` block describing the inherited evidence.

    Parameters
    ----------
    devices : list[dict]
        The full device list (e.g. from enriched_final.json).
    expand_from_openfda : bool
        If True, also query openFDA to discover additional family members
        beyond those in our local dataset.

    Returns
    -------
    list[dict]
        The same device list, mutated in-place with ``family_evidence`` added
        to qualifying devices.
    """
    print(f"Building product_code family graph for {len(devices)} devices...")
    graph = build_family_graph(devices)
    print(f"  Found {len(graph)} distinct product_code families")

    if expand_from_openfda:
        print("Expanding families from openFDA 510(k) database...")
        expand_families_from_openfda(graph)

    # Build a quick lookup: k_number -> device
    k_lookup: dict[str, dict] = {}
    for dev in devices:
        k_num = dev.get("fda_submission_number", "")
        if k_num:
            k_lookup[k_num] = dev

    tagged = 0
    for dev in devices:
        product_code = dev.get("product_code", "")
        if not product_code or product_code not in graph:
            continue

        family = graph[product_code]
        n_direct = _count_direct_evidence(dev)

        # Only tag devices that lack direct evidence themselves
        if n_direct > 0:
            continue

        # Find family members WITH evidence (excluding self)
        self_k = dev.get("fda_submission_number", "")
        siblings_with_evidence = [
            m for m in family["members_with_evidence"]
            if m["k_number"] != self_k
        ]

        if not siblings_with_evidence:
            continue

        total_inherited_pubs = sum(
            m["n_total"] for m in siblings_with_evidence
        )

        dev["family_evidence"] = {
            "product_code": product_code,
            "family_size": family["family_size"],
            "fda_family_size": family.get("fda_family_size"),
            "siblings_with_evidence": siblings_with_evidence,
            "inherited_publication_count": total_inherited_pubs,
            "note": (
                f"No direct publications found for this device, but "
                f"{len(siblings_with_evidence)} device(s) in the same "
                f"product_code family ({product_code}) have "
                f"{total_inherited_pubs} publication(s). These devices "
                f"share the same FDA classification and intended use."
            ),
        }
        tagged += 1

    print(
        f"  Tagged {tagged} device(s) with inherited family evidence "
        f"(out of {len(devices)} total)"
    )

    return devices


# ---------------------------------------------------------------------------
# Summary / reporting helpers
# ---------------------------------------------------------------------------


def summarize_families(graph: dict) -> None:
    """Print a human-readable summary of product_code families."""
    families_with_evidence = {
        pc: f for pc, f in graph.items()
        if f["members_with_evidence"]
    }
    families_without = {
        pc: f for pc, f in graph.items()
        if not f["members_with_evidence"]
    }

    print(f"\nProduct Code Family Summary")
    print(f"{'='*60}")
    print(f"Total families:              {len(graph)}")
    print(f"Families with evidence:      {len(families_with_evidence)}")
    print(f"Families without evidence:   {len(families_without)}")
    print()

    # Show multi-member families (most interesting for predicate analysis)
    multi = {
        pc: f for pc, f in graph.items() if f["family_size"] > 1
    }
    if multi:
        print(f"Multi-device families ({len(multi)}):")
        for pc, fam in sorted(
            multi.items(), key=lambda x: x[1]["family_size"], reverse=True
        ):
            evidence_flag = (
                "  [has evidence]" if fam["members_with_evidence"] else ""
            )
            names = [m["device_name"] for m in fam["members"]]
            print(
                f"  {pc} ({fam['family_size']} devices){evidence_flag}"
            )
            for name in names:
                print(f"    - {name}")
        print()

    # Show singleton families with no evidence (evidence desert)
    singletons_no_ev = [
        (pc, f) for pc, f in graph.items()
        if f["family_size"] == 1 and not f["members_with_evidence"]
    ]
    if singletons_no_ev:
        print(
            f"Singleton families with no evidence: "
            f"{len(singletons_no_ev)}"
        )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------


def _find_input_file() -> Path:
    """Locate the best available enriched data file."""
    # Prefer enriched_final.json, fall back to latest checkpoint
    final = DATA_DIR / "enriched_final.json"
    if final.exists():
        return final

    checkpoints = sorted(DATA_DIR.glob("enriched_checkpoint_*.json"))
    if checkpoints:
        return checkpoints[-1]

    raise FileNotFoundError(
        f"No enriched data found in {DATA_DIR}. "
        "Run the enrichment pipeline first."
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Trace 510(k) product_code family evidence chains."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to enriched JSON (default: auto-detect in data/)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output path (default: data/enriched_with_families.json)",
    )
    parser.add_argument(
        "--expand-openfda",
        action="store_true",
        help="Query openFDA to discover additional family members",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print family summary without modifying data",
    )
    args = parser.parse_args()

    # Load data
    input_path = Path(args.input) if args.input else _find_input_file()
    print(f"Loading devices from {input_path}")
    with open(input_path) as f:
        devices = json.load(f)
    print(f"  Loaded {len(devices)} devices")

    if args.summary_only:
        graph = build_family_graph(devices)
        if args.expand_openfda:
            expand_families_from_openfda(graph)
        summarize_families(graph)
        return

    # Enrich
    devices = enrich_with_family_evidence(
        devices, expand_from_openfda=args.expand_openfda
    )

    # Save
    output_path = Path(args.output) if args.output else (
        DATA_DIR / "enriched_with_families.json"
    )
    with open(output_path, "w") as f:
        json.dump(devices, f, indent=2)
    print(f"\nSaved to {output_path}")

    # Quick stats
    n_with_family = sum(
        1 for d in devices if d.get("family_evidence")
    )
    n_with_direct = sum(
        1 for d in devices if _count_direct_evidence(d) > 0
    )
    n_with_any = sum(
        1 for d in devices if _count_all_evidence(d) > 0
    )
    print(f"\nEvidence coverage:")
    print(f"  Direct evidence:    {n_with_direct}/{len(devices)}")
    print(f"  Any evidence:       {n_with_any}/{len(devices)}")
    print(f"  + Family evidence:  {n_with_family}/{len(devices)}")
    print(
        f"  Total covered:      "
        f"{n_with_any + n_with_family}/{len(devices)} "
        f"(may overlap)"
    )


if __name__ == "__main__":
    main()

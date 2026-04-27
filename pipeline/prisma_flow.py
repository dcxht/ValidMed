"""Generate PRISMA-like evidence flow statistics from enriched pipeline data."""

import json
import sys
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def analyze_flow(data_path: str):
    with open(data_path) as f:
        devices = json.load(f)

    total = len(devices)

    # Count devices by evidence tier
    has_direct = 0       # At least one "direct" match
    has_company_only = 0 # Only "company" matches, no direct
    has_any = 0          # Any PubMed evidence
    has_none = 0         # No PubMed evidence

    # Article counts
    total_direct_articles = 0
    total_company_articles = 0

    # Study type counts across direct articles
    study_types = Counter()

    for d in devices:
        evidence = d.get("evidence", [])
        direct = [e for e in evidence if e.get("match_tier") == "direct"]
        company = [e for e in evidence if e.get("match_tier") == "company"]

        total_direct_articles += len(direct)
        total_company_articles += len(company)

        if direct:
            has_direct += 1
            has_any += 1
            for e in direct:
                study_types[e.get("study_type", "other")] += 1
        elif company:
            has_company_only += 1
            has_any += 1
        else:
            has_none += 1

    flow = {
        "total_devices": total,
        "with_direct_evidence": has_direct,
        "with_company_only": has_company_only,
        "with_any_evidence": has_any,
        "with_no_evidence": has_none,
        "total_direct_articles": total_direct_articles,
        "total_company_articles": total_company_articles,
        "study_types_in_direct": dict(study_types.most_common()),
        "pct_direct": round(has_direct / total * 100, 1),
        "pct_any": round(has_any / total * 100, 1),
        "pct_none": round(has_none / total * 100, 1),
    }

    # Print flow diagram
    print(f"""
PRISMA-like Evidence Flow — ValidMed
{'=' * 55}

  FDA AI/ML Device List
  [{total} devices]
       |
       v
  PubMed Multi-Tier Search
  (Tier 0: aliases, Tier 1: device name,
   Tier 2: company+device, Tier 3: company AI research)
       |
       +---> Direct evidence (device name in publication)
       |     [{has_direct} devices ({flow['pct_direct']}%)]
       |     [{total_direct_articles} total articles]
       |
       +---> Company-tier only (no direct match)
       |     [{has_company_only} devices ({has_company_only/total*100:.1f}%)]
       |     [{total_company_articles} total articles]
       |
       +---> No PubMed evidence
             [{has_none} devices ({flow['pct_none']}%)]

  Study types in direct evidence:
""")
    for st, count in study_types.most_common():
        print(f"    {st:25s}: {count:5d} articles")

    # Save
    out = DATA_DIR / "prisma_flow.json"
    with open(out, "w") as f:
        json.dump(flow, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(DATA_DIR / "enriched_final.json")
    analyze_flow(path)

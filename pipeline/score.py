"""Compute evidence scores for devices.

Scoring is transparent and decomposable — every component is visible.
Score range: 0-100.

Changes from v1:
- Removed independence component (is_manufacturer_authored was never populated)
- Removed safety "free points" (no MAUDE data ≠ safe)
- Trust level uses only reliably available data (match_tier, study_type, count)
- Score reweighted: evidence 45, quality 25, safety 15, trials 15
"""

STUDY_TYPE_SCORES = {
    "RCT": 10,
    "clinical_trial": 7,
    "clinical_study": 6,
    "meta_analysis": 9,
    "systematic_review": 7,
    "other": 2,
    "case_report": 1,
    "review": 1,
}


def compute_score(
    evidence: list[dict],
    safety_events: list[dict],
    recalls: list[dict],
    trials: list[dict],
) -> dict:
    """Compute a transparent evidence score for a device.

    Returns a dict with total score and component breakdown.
    """
    # Only count direct-match evidence for scoring
    # Company-tier is shown separately but doesn't inflate the score
    # "maybe" relevance articles count at 50% weight (2 maybe = 1 confirmed)
    direct_confirmed = [e for e in evidence if e.get("match_tier") == "direct" and e.get("relevance") != "maybe"]
    direct_maybe = [e for e in evidence if e.get("match_tier") == "direct" and e.get("relevance") == "maybe"]
    direct_evidence = direct_confirmed + direct_maybe  # All direct for study type analysis
    all_evidence = evidence

    # Weighted count: confirmed = 1, maybe = 0.5
    n_direct = len(direct_confirmed) + len(direct_maybe) // 2
    n_total = len(all_evidence)

    # 1. Evidence count (0-45 points) — based on DIRECT matches only
    if n_direct == 0:
        ev_score = 0
    elif n_direct <= 2:
        ev_score = 12
    elif n_direct <= 5:
        ev_score = 24
    elif n_direct <= 10:
        ev_score = 35
    else:
        ev_score = 45

    # 2. Study quality (0-25 points) — best study type in direct evidence
    if direct_evidence:
        best_quality = max(
            STUDY_TYPE_SCORES.get(e.get("study_type", "other"), 1)
            for e in direct_evidence
        )
        quality_score = min(round(best_quality * 2.5), 25)
    else:
        quality_score = 0

    # 3. Safety (0-15 points)
    # No data = 0 points (unknown, not safe)
    # Clean record with data = 15 points
    # Events/recalls = deductions from 15
    n_events = len(safety_events)
    n_recalls = len(recalls)
    deaths = sum(1 for e in safety_events if e.get("event_type") == "Death")
    injuries = sum(1 for e in safety_events if e.get("event_type") == "Injury")

    if n_events == 0 and n_recalls == 0:
        # No safety data — score is 0 (unknown), not 15 (safe)
        safety_score = 0
    else:
        # Has safety data — start at 15, deduct for problems
        safety_score = 15
        safety_score -= min(deaths * 5, 10)
        safety_score -= min(injuries * 2, 5)
        safety_score -= min(n_recalls * 3, 6)
        safety_score = max(safety_score, 0)

    # 4. Trial activity (0-15 points)
    if not trials:
        trial_score = 0
    else:
        completed_with_results = sum(1 for t in trials if t.get("has_results"))
        completed = sum(
            1 for t in trials if t.get("status") in ("COMPLETED", "Completed")
        )

        if completed_with_results >= 1:
            trial_score = 15
        elif completed >= 1:
            trial_score = 10
        else:
            trial_score = 5  # At least registered

    total = ev_score + quality_score + safety_score + trial_score

    # Compute trust level (uses only reliable data)
    trust_level = _compute_trust_level(direct_evidence, all_evidence, trials)

    return {
        "total": total,
        "trust_level": trust_level,
        "evidence_volume": ev_score,
        "study_quality": quality_score,
        "safety": safety_score,
        "trials": trial_score,
        "detail": {
            "n_direct_publications": n_direct,
            "n_company_publications": n_total - n_direct,
            "n_publications": n_total,
            "n_safety_events": n_events,
            "n_deaths": deaths,
            "n_injuries": injuries,
            "n_recalls": n_recalls,
            "n_trials": len(trials),
            "n_trials_with_results": sum(1 for t in trials if t.get("has_results")),
        },
    }


def _compute_trust_level(
    direct_evidence: list[dict],
    all_evidence: list[dict],
    trials: list[dict],
) -> str:
    """Compute trust level using only reliably available data.

    Does NOT use is_manufacturer_authored (never populated).
    Based on: direct match count, study types, trial results.

    Levels:
      "strong"   — Multiple direct studies including RCT or clinical trial
      "moderate" — Multiple direct studies or clinical trial evidence
      "limited"  — Some evidence (direct or company-tier)
      "none"     — No published evidence found
    """
    if not all_evidence:
        return "none"

    n_direct = len(direct_evidence)
    direct_types = {e.get("study_type") for e in direct_evidence}
    has_rct = "RCT" in direct_types
    has_clinical = "clinical_trial" in direct_types or "clinical_study" in direct_types or has_rct
    has_meta = "meta_analysis" in direct_types or "systematic_review" in direct_types
    trial_results = any(t.get("has_results") for t in trials)

    # Strong: multiple direct studies with strong designs
    if n_direct >= 3 and (has_rct or (has_clinical and has_meta) or trial_results):
        return "strong"

    # Moderate: meaningful direct evidence
    if n_direct >= 3:
        return "moderate"
    if n_direct >= 2 and has_clinical:
        return "moderate"

    # Limited: some evidence exists
    if n_direct >= 1:
        return "limited"
    if all_evidence:
        return "limited"

    return "none"

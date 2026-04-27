"""Enrich devices with clinical trial data from ClinicalTrials.gov v2 API.

Pass-2 enrichment script: loads enriched_final.json, adds trial data to each
device, and saves the result back.
"""

import json
import logging
import time
from pathlib import Path

import httpx

from config import CT_GOV_BASE, CT_GOV_DELAY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "ValidMed-Pipeline/1.0 (academic research; contact: contact@validmed.org)",
    "Accept": "application/json",
}

FIELDS = ",".join([
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.startDateStruct",
    "protocolSection.statusModule.completionDateStruct",
    "protocolSection.sponsorCollaboratorsModule.leadSponsor",
    "protocolSection.designModule.phases",
    "protocolSection.designModule.enrollmentInfo",
    "hasResults",
])

DATA_DIR = Path(__file__).resolve().parent / "data"


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

def _request_with_retry(url: str, params: dict, max_attempts: int = 3) -> httpx.Response | None:
    """GET with exponential backoff. Returns Response on success, None on failure."""
    for attempt in range(1, max_attempts + 1):
        try:
            resp = httpx.get(url, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            log.warning("Attempt %d/%d got HTTP %d for %s", attempt, max_attempts, status, url)
            if status == 403 and attempt < max_attempts:
                wait = 2 ** attempt  # 2, 4, 8 seconds
                log.info("Retrying in %ds (exponential backoff)...", wait)
                time.sleep(wait)
            elif attempt < max_attempts:
                time.sleep(2 ** attempt)
            else:
                log.error("All %d attempts failed (last status %d).", max_attempts, status)
                return None
        except httpx.RequestError as exc:
            log.warning("Attempt %d/%d request error: %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                time.sleep(2 ** attempt)
            else:
                log.error("All %d attempts failed due to request errors.", max_attempts)
                return None
    return None


# ---------------------------------------------------------------------------
# Search strategies
# ---------------------------------------------------------------------------

def _parse_studies(data: dict) -> list[dict]:
    """Extract structured trial records from the v2 API response."""
    results = []
    for study in data.get("studies", []):
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
        design = proto.get("designModule", {})

        start = status_mod.get("startDateStruct", {})
        completion = status_mod.get("completionDateStruct", {})
        lead = sponsor_mod.get("leadSponsor", {})
        phases = design.get("phases", [])
        enrollment = design.get("enrollmentInfo", {})

        results.append({
            "nct_id": ident.get("nctId", ""),
            "title": ident.get("briefTitle", ""),
            "status": status_mod.get("overallStatus", ""),
            "has_results": study.get("hasResults", False),
            "start_date": start.get("date"),
            "completion_date": completion.get("date"),
            "sponsor": lead.get("name", ""),
            "phase": ", ".join(phases) if phases else None,
            "enrollment": enrollment.get("count"),
        })
    return results


def search_trials(device_name: str, company: str, max_results: int = 20) -> list[dict]:
    """Search ClinicalTrials.gov for trials related to a device.

    Strategy 1: search by device name (+ company for relevance).
    Strategy 2 (fallback): search by sponsor/company name only.
    Strategy 3 (fallback): return a manual-follow-up URL.
    """
    url = f"{CT_GOV_BASE}/studies"

    # --- Strategy 1: device-name search ---
    query = f'"{device_name}"'
    if company:
        query += f' OR "{company}" "{device_name}"'

    params = {
        "query.term": query,
        "pageSize": max_results,
        "fields": FIELDS,
    }

    log.info("Strategy 1 — searching by device name: %s", device_name)
    resp = _request_with_retry(url, params)
    if resp is not None:
        results = _parse_studies(resp.json())
        if results:
            log.info("  Found %d trial(s) via device-name search.", len(results))
            return results
        log.info("  Device-name search returned 0 results; trying sponsor fallback.")

    # --- Strategy 2: sponsor/company search ---
    if company:
        sponsor_params = {
            "query.spons": company,
            "pageSize": max_results,
            "fields": FIELDS,
        }
        log.info("Strategy 2 — searching by sponsor: %s", company)
        resp = _request_with_retry(url, sponsor_params)
        if resp is not None:
            results = _parse_studies(resp.json())
            if results:
                log.info("  Found %d trial(s) via sponsor search.", len(results))
                return results
            log.info("  Sponsor search returned 0 results.")

    # --- Strategy 3: manual follow-up URL ---
    search_term = device_name or company or "unknown"
    manual_url = f"https://clinicaltrials.gov/search?term={search_term.replace(' ', '+')}"
    log.warning(
        "All API strategies failed for '%s' (%s). Manual follow-up URL: %s",
        device_name, company, manual_url,
    )
    return [{
        "_manual_followup": True,
        "search_url": manual_url,
        "note": f"API search failed for device='{device_name}', company='{company}'. Visit URL to search manually.",
    }]


def enrich_device(device_name: str, company: str) -> list[dict]:
    """Full ClinicalTrials.gov enrichment for one device."""
    trials = search_trials(device_name, company)
    time.sleep(CT_GOV_DELAY)
    return trials


# ---------------------------------------------------------------------------
# Standalone pass-2 enrichment
# ---------------------------------------------------------------------------

def run_pass2(input_path: Path | None = None, output_path: Path | None = None) -> None:
    """Load enriched_final.json, add trial data to each device, save result."""
    input_path = input_path or DATA_DIR / "enriched_final.json"
    output_path = output_path or DATA_DIR / "enriched_final.json"

    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        raise FileNotFoundError(input_path)

    log.info("Loading devices from %s", input_path)
    devices = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(devices, list):
        log.error("Expected a JSON array of device objects.")
        raise ValueError("enriched_final.json must contain a JSON array")

    total = len(devices)
    log.info("Enriching %d devices with ClinicalTrials.gov data...", total)

    for idx, device in enumerate(devices, 1):
        name = device.get("device_name") or device.get("name") or ""
        company = device.get("company") or device.get("sponsor") or ""

        if not name and not company:
            log.warning("[%d/%d] Skipping device with no name or company.", idx, total)
            device["clinical_trials"] = []
            continue

        log.info("[%d/%d] %s (%s)", idx, total, name, company)
        device["clinical_trials"] = enrich_device(name, company)

    log.info("Saving enriched data to %s", output_path)
    output_path.write_text(json.dumps(devices, indent=2, default=str), encoding="utf-8")
    log.info("Done. Enriched %d devices.", total)


if __name__ == "__main__":
    run_pass2()

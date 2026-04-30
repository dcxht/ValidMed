"""Enrich devices with MAUDE adverse events and recalls from openFDA."""

import re
import time

import httpx

from config import OPENFDA_API_KEY, OPENFDA_BASE, OPENFDA_DELAY


def _build_params(search: str, limit: int = 100) -> dict:
    params = {"search": search, "limit": limit}
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY
    return params


def _normalize(text: str) -> str:
    return re.sub(r"[™®©]", "", text).strip().lower()


def fetch_maude_events(device_name: str, company: str) -> list[dict]:
    """Fetch adverse event reports from MAUDE for a device."""
    # Search by exact brand name AND manufacturer to avoid name collisions
    # (e.g. "SYNAPSE" matching both PACS software and spinal screws)
    if company:
        # Extract core company name (first meaningful word)
        company_clean = company.split(",")[0].strip()
        search = f'device.brand_name:"{device_name}" AND device.manufacturer_d_name:"{company_clean}"'
    else:
        search = f'device.brand_name:"{device_name}"'

    params = _build_params(search)
    try:
        resp = httpx.get(
            f"{OPENFDA_BASE}/device/event.json", params=params, timeout=30
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        return []

    data = resp.json()

    # Deduplicate by report_number (MAUDE has initial + followup entries)
    seen = set()
    results = []
    for event in data.get("results", []):
        report_num = event.get("report_number", "")
        if not report_num or report_num in seen:
            continue
        seen.add(report_num)

        # Verify the device in this event actually matches our device
        if not _event_matches_device(event, device_name, company):
            continue

        results.append({
            "report_number": report_num,
            "event_type": event.get("event_type", ""),
            "date_of_event": event.get("date_of_event"),
            "narrative_text": _extract_narrative(event),
            "patient_outcome": _extract_outcome(event),
            "source_type": event.get("source_type", ""),
        })

    return results


def _event_matches_device(event: dict, device_name: str, company: str) -> bool:
    """Verify the MAUDE event actually involves our specific device."""
    name_lower = _normalize(device_name)
    company_lower = _normalize(company.split(",")[0]) if company else ""

    for device in event.get("device", []):
        brand = _normalize(device.get("brand_name", ""))
        mfr = _normalize(device.get("manufacturer_d_name", ""))

        # Brand name must match (substring ok for cases like "LOGIQ E10s" matching "LOGIQ E10")
        if name_lower in brand or brand in name_lower:
            # If we have a company, manufacturer should also match
            if not company_lower:
                return True
            if company_lower in mfr or mfr in company_lower:
                return True

    return False


def _extract_narrative(event: dict) -> str:
    texts = event.get("mdr_text", [])
    for t in texts:
        if t.get("text"):
            return t["text"][:2000]
    return ""


def _extract_outcome(event: dict) -> str:
    patients = event.get("patient", [])
    if patients:
        outcomes = patients[0].get("sequence_number_outcome", [])
        return ", ".join(outcomes) if outcomes else ""
    return ""


def fetch_recalls(k_number: str = "", device_name: str = "") -> list[dict]:
    """Fetch recall records for a device."""
    if k_number:
        search = f'k_numbers:"{k_number}"'
    elif device_name:
        search = f'product_description:"{device_name}"'
    else:
        return []

    params = _build_params(search, limit=20)
    try:
        resp = httpx.get(
            f"{OPENFDA_BASE}/device/recall.json", params=params, timeout=30
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        return []

    data = resp.json()

    # Deduplicate by recall number
    seen = set()
    results = []
    for recall in data.get("results", []):
        recall_num = recall.get("res_event_number", "")
        if not recall_num or recall_num in seen:
            continue
        seen.add(recall_num)

        results.append({
            "recall_number": recall_num,
            "reason": recall.get("reason_for_recall", ""),
            "date_initiated": recall.get("event_date_initiated"),
            "status": recall.get("recall_status", ""),
            "root_cause": recall.get("root_cause_description", ""),
            "product_description": recall.get("product_description", "")[:500],
        })

    return results


def enrich_device(k_number: str, device_name: str, company: str) -> dict:
    """Full openFDA enrichment for one device."""
    events = fetch_maude_events(device_name, company)
    time.sleep(OPENFDA_DELAY)

    recalls = fetch_recalls(k_number=k_number, device_name=device_name)
    time.sleep(OPENFDA_DELAY)

    return {"safety_events": events, "recalls": recalls}


if __name__ == "__main__":
    result = enrich_device("K213205", "Viz LVO", "Viz.ai")
    print(f"MAUDE events: {len(result['safety_events'])}")
    print(f"Recalls: {len(result['recalls'])}")

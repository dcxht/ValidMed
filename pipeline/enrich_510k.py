"""Enrich devices with 510(k) clearance details from openFDA.

Adds: device_class, clearance_type, predicate device, summary availability,
and direct link to the FDA summary PDF.
"""

import time

import httpx

from config import OPENFDA_API_KEY, OPENFDA_BASE, OPENFDA_DELAY


def fetch_510k_details(k_number: str) -> dict | None:
    """Fetch 510(k) clearance details for a device."""
    if not k_number:
        return None

    params = {"search": f'k_number:"{k_number}"', "limit": 1}
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY

    for attempt in range(3):
        try:
            resp = httpx.get(
                f"{OPENFDA_BASE}/device/510k.json", params=params, timeout=30
            )
            if resp.status_code == 404:
                return None
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            break
        except Exception:
            time.sleep(2 ** attempt)
    else:
        return None

    results = resp.json().get("results", [])
    if not results:
        return None

    r = results[0]
    openfda = r.get("openfda", {})

    # Construct link to FDA summary PDF
    summary_url = f"https://www.accessdata.fda.gov/cdrh_docs/pdf{k_number[1:3]}/{k_number}.pdf"

    # Get device class from openfda nested fields
    device_class = None
    if openfda.get("device_class"):
        device_class = openfda["device_class"]
        if isinstance(device_class, list):
            device_class = device_class[0] if device_class else None

    return {
        "device_class": device_class,
        "clearance_type": r.get("clearance_type"),
        "decision_code": r.get("decision_code"),
        "statement_or_summary": r.get("statement_or_summary"),
        "summary_url": summary_url if r.get("statement_or_summary") == "Summary" else None,
        "date_received": r.get("date_received"),
        "expedited_review": r.get("expedited_review_flag") == "Y",
        "third_party_review": r.get("third_party_flag") == "Y",
    }


def enrich_batch(devices: list[dict]) -> list[dict]:
    """Add 510(k) details to a list of enriched device records."""
    for i, device in enumerate(devices):
        k_number = device.get("fda_submission_number", "")
        if not k_number.startswith("K"):
            # Skip De Novo (DEN) or PMA submissions — different API
            continue

        details = fetch_510k_details(k_number)
        time.sleep(OPENFDA_DELAY)

        if details:
            device["clearance_details"] = details
            # Also set device_class at top level for easy access
            if details.get("device_class"):
                device["device_class"] = details["device_class"]

        if (i + 1) % 100 == 0:
            print(f"  510(k) enrichment: {i+1}/{len(devices)}", flush=True)

    return devices


if __name__ == "__main__":
    # Test
    details = fetch_510k_details("K253532")
    if details:
        for k, v in details.items():
            print(f"  {k}: {v}")
    else:
        print("No results")

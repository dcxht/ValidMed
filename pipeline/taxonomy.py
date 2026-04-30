"""Clinical use case taxonomy for FDA AI/ML devices.

Maps product codes and device name patterns to human-readable clinical use cases.
This makes ValidMed browsable by physicians: "show me all stroke triage tools."
"""

import re

# Product code -> clinical use case mapping
# Based on FDA device classification definitions
PRODUCT_CODE_MAP = {
    # Radiology - Triage & Detection
    "QAS": "Triage & Notification",
    "QFM": "Lesion Prioritization",
    "QBS": "Fracture Detection",
    "QDQ": "Cancer Detection (Radiology)",
    "POK": "Cancer Detection (Radiology)",
    "QNP": "GI Lesion Detection",

    # Radiology - Image Processing & Enhancement
    "QIH": "Image Processing & Enhancement",
    "LLZ": "Image Processing & Enhancement",
    "MYN": "Image Analysis",
    "LNH": "MRI Systems & Reconstruction",
    "JAK": "CT Systems & Reconstruction",
    "KPS": "Nuclear Medicine & PET",

    # Radiology - Treatment Planning
    "QKB": "Radiation Therapy Planning",
    "MUJ": "Radiation Therapy Planning",

    # Cardiovascular
    "DQK": "Cardiac Diagnostics",

    # Ultrasound
    "IYN": "Ultrasound Systems",

    # Gastroenterology
    "QNP": "GI Lesion Detection",

    # Orthopedic / Neuro
    "OLO": "Surgical Navigation",

    # Sleep / Anesthesiology
    "MNR": "Sleep & Respiratory Monitoring",
}

# Name-based patterns for more specific categorization
# These override the product code mapping when matched
NAME_PATTERNS = [
    # Stroke
    (r"stroke|lvo|large vessel|ischemic brain|hemorrhage|ich\b", "Stroke Triage & Detection"),
    # Mammography
    (r"mammo|breast|tomosynthesis|dbt", "Mammography & Breast Imaging"),
    # Lung
    (r"lung|pulmonary|chest.*(x-ray|xray|ct)|nodule|pe\b|pneumo", "Lung & Chest Imaging"),
    # Cardiac
    (r"cardiac|cardio|echo|echocardiogra|ekg|ecg|arrhythm|afib|atrial|heart|coronary", "Cardiac Diagnostics"),
    # Retinal / Ophthalmic
    (r"retin|fundus|diabetic retinopathy|ophthalm|eye|oct\b|macula", "Retinal & Ophthalmic"),
    # Pathology / Histology
    (r"pathol|histol|cytol|biopsy|whole.slide|wsi", "Digital Pathology"),
    # Dental
    (r"dental|dentin|caries|periodon|oral", "Dental"),
    # Fracture
    (r"fracture|bone|musculoskeletal|msk|orthop", "Fracture & MSK Detection"),
    # Colonoscopy / GI
    (r"colon|polyp|endoscop|gastro|gi\b", "GI & Endoscopy"),
    # Radiation therapy
    (r"radiation therapy|radiotherapy|contour|treatment plan|linac", "Radiation Therapy Planning"),
    # Ultrasound guidance
    (r"ultrasound|sono|doppler", "Ultrasound"),
    # Surgical
    (r"surgical|navigation|robotic|spine|spinal|stereotax", "Surgical Navigation & Robotics"),
    # Sleep
    (r"sleep|apnea|psg|polysom|respiratory.*monitor", "Sleep & Respiratory"),
    # Dermatology
    (r"derm|skin|lesion.*skin|melanom", "Dermatology"),
    # Liver
    (r"liver|hepat|fibrosis.*liver|steatosis", "Liver Imaging"),
    # Prostate
    (r"prostate|psa", "Prostate Imaging"),
    # Brain (general, after stroke)
    (r"brain|neuro|intracranial|cranial|mri.*brain|alzheimer|dementia", "Neuroimaging"),
]


def classify_device(device_name: str, product_code: str, specialty: str) -> str:
    """Classify a device into a clinical use case.

    Priority:
    1. Name-based pattern matching (most specific)
    2. Product code mapping
    3. Specialty-based fallback
    """
    name_lower = device_name.lower() if device_name else ""

    # Try name patterns first
    for pattern, use_case in NAME_PATTERNS:
        if re.search(pattern, name_lower, re.IGNORECASE):
            return use_case

    # Try product code
    if product_code and product_code in PRODUCT_CODE_MAP:
        return PRODUCT_CODE_MAP[product_code]

    # Fallback to specialty
    specialty_fallback = {
        "Radiology": "General Radiology AI",
        "Cardiovascular": "Cardiac Diagnostics",
        "Neurology": "Neuroimaging",
        "Gastroenterology-Urology": "GI & Endoscopy",
        "Ophthalmic": "Retinal & Ophthalmic",
        "Pathology": "Digital Pathology",
        "Hematology": "Hematology",
        "Anesthesiology": "Sleep & Respiratory",
        "Dental": "Dental",
        "Clinical Chemistry": "Clinical Chemistry",
        "Microbiology": "Microbiology",
    }
    return specialty_fallback.get(specialty, "Other")


def classify_all(devices: list[dict]) -> list[dict]:
    """Add clinical_use_case field to all devices."""
    for d in devices:
        d["clinical_use_case"] = classify_device(
            d.get("device_name", ""),
            d.get("product_code", ""),
            d.get("specialty_panel", ""),
        )
    return devices


if __name__ == "__main__":
    import json
    from collections import Counter

    with open("data/enriched_checkpoint_950.json") as f:
        data = json.load(f)

    data = classify_all(data)

    use_cases = Counter(d["clinical_use_case"] for d in data)
    print(f"Clinical use cases ({len(use_cases)} categories):\n")
    for uc, count in use_cases.most_common():
        zero = sum(1 for d in data if d["clinical_use_case"] == uc
                   and d.get("score", {}).get("detail", {}).get("n_publications", 0) == 0)
        print(f"  {uc}: {count} devices ({zero} zero evidence)")

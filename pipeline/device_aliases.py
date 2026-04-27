"""
device_aliases.py — Curated alias mapping for top 50 FDA-cleared AI/ML medical devices.

Provides canonical name-to-alias mappings and search query generators for
PubMed / OpenAlex evidence retrieval. Each entry stores the FDA-registered
name, commercial names, common literature references, company name
variations, and legacy/rebranded names.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Master alias dictionary
# Keys   : FDA-registered / canonical device name (lowercase, stripped)
# Values : dict with the following optional fields:
#   fda_name        – name as it appears in the FDA AI/ML device list
#   commercial_names – marketing / brand names
#   research_refs    – names commonly used in journal articles
#   company_names    – manufacturer name variations
#   legacy_names     – former names, pre-rebrand names
#   abbreviations    – short-hand / acronyms used in literature
# ---------------------------------------------------------------------------

DEVICE_ALIASES: Dict[str, Dict[str, List[str]]] = {

    # ======================================================================
    # STROKE / NEURO
    # ======================================================================

    "viz lvo": {
        "fda_name": ["Viz LVO"],
        "commercial_names": ["Viz LVO", "Viz ContaCT", "Viz.ai LVO"],
        "research_refs": [
            "Viz LVO large vessel occlusion",
            "Viz ContaCT CT angiography",
            "Viz.ai stroke triage",
            "Viz.ai automated LVO detection",
        ],
        "company_names": ["Viz.ai", "Viz.ai Inc", "Viz AI"],
        "legacy_names": ["ContaCT"],
        "abbreviations": ["LVO"],
    },

    "viz contact": {
        "fda_name": ["Viz ContaCT"],
        "commercial_names": ["Viz ContaCT", "Viz.ai ContaCT"],
        "research_refs": [
            "Viz ContaCT CT perfusion",
            "Viz.ai stroke notification",
            "ContaCT automated stroke detection",
        ],
        "company_names": ["Viz.ai", "Viz.ai Inc"],
        "legacy_names": ["ContaCT"],
        "abbreviations": [],
    },

    "rapid lvo": {
        "fda_name": ["RAPID LVO"],
        "commercial_names": ["RAPID LVO", "RAPID Large Vessel Occlusion"],
        "research_refs": [
            "RAPID LVO detection",
            "iSchemaView RAPID LVO",
            "RAPID AI large vessel occlusion",
        ],
        "company_names": ["iSchemaView", "iSchemaView Inc", "RapidAI", "Rapid AI"],
        "legacy_names": ["iSchemaView RAPID"],
        "abbreviations": ["RAPID"],
    },

    "rapid ctp": {
        "fda_name": ["RAPID CTP"],
        "commercial_names": ["RAPID CTP", "RAPID CT Perfusion", "RAPID"],
        "research_refs": [
            "RAPID perfusion imaging",
            "RAPID automated CT perfusion",
            "RAPID ischemic core estimation",
            "RAPID penumbra mismatch",
            "iSchemaView RAPID perfusion",
        ],
        "company_names": ["iSchemaView", "iSchemaView Inc", "RapidAI", "Rapid AI"],
        "legacy_names": ["RAPID software", "iSchemaView RAPID"],
        "abbreviations": ["RAPID", "CTP"],
    },

    "brainomix e-stroke": {
        "fda_name": ["Brainomix e-Stroke"],
        "commercial_names": ["e-Stroke", "e-Stroke Suite", "Brainomix e-Stroke Suite"],
        "research_refs": [
            "Brainomix e-Stroke",
            "e-Stroke automated ASPECTS",
            "Brainomix AI stroke imaging",
            "e-Stroke CT perfusion",
            "Brainomix e-CTA",
        ],
        "company_names": ["Brainomix", "Brainomix Ltd", "Brainomix Limited"],
        "legacy_names": ["e-ASPECTS", "e-CTA"],
        "abbreviations": ["e-Stroke"],
    },

    "zebra healthich": {
        "fda_name": ["HealthICH"],
        "commercial_names": ["HealthICH", "Zebra-Med HealthICH", "Zebra HealthICH"],
        "research_refs": [
            "Zebra Medical Vision intracranial hemorrhage",
            "HealthICH intracranial hemorrhage detection",
            "Zebra-Med ICH AI",
        ],
        "company_names": [
            "Zebra Medical Vision",
            "Zebra-Med",
            "Zebra Medical Vision Ltd",
            "Nanox AI",
        ],
        "legacy_names": ["Zebra Medical Vision HealthICH"],
        "abbreviations": ["ICH"],
    },

    "aidoc briefcase ich": {
        "fda_name": ["Aidoc BriefCase for Intracranial Hemorrhage"],
        "commercial_names": [
            "Aidoc BriefCase ICH",
            "Aidoc ICH",
            "BriefCase Intracranial Hemorrhage",
        ],
        "research_refs": [
            "Aidoc intracranial hemorrhage triage",
            "Aidoc BriefCase ICH detection",
            "Aidoc AI hemorrhage CT",
        ],
        "company_names": ["Aidoc", "Aidoc Medical", "Aidoc Ltd"],
        "legacy_names": [],
        "abbreviations": ["ICH"],
    },

    # ======================================================================
    # RETINAL / OPHTHALMIC
    # ======================================================================

    "idx-dr": {
        "fda_name": ["IDx-DR"],
        "commercial_names": [
            "IDx-DR",
            "LumineticsCore",
            "Luminetics Core",
            "Digital Diagnostics IDx-DR",
        ],
        "research_refs": [
            "IDx-DR autonomous diabetic retinopathy",
            "IDx-DR diabetic retinopathy screening",
            "LumineticsCore diabetic retinopathy",
            "autonomous AI diabetic retinopathy detection",
            "Digital Diagnostics diabetic retinopathy",
        ],
        "company_names": [
            "Digital Diagnostics",
            "Digital Diagnostics Inc",
            "IDx Technologies",
            "IDx LLC",
        ],
        "legacy_names": ["IDx-DR"],
        "abbreviations": ["IDx-DR"],
    },

    "lumineticscore": {
        "fda_name": ["LumineticsCore"],
        "commercial_names": ["LumineticsCore", "Luminetics Core"],
        "research_refs": [
            "LumineticsCore diabetic retinopathy",
            "Digital Diagnostics LumineticsCore",
        ],
        "company_names": ["Digital Diagnostics", "Digital Diagnostics Inc"],
        "legacy_names": ["IDx-DR"],
        "abbreviations": [],
    },

    "eyeart": {
        "fda_name": ["EyeArt"],
        "commercial_names": ["EyeArt", "EyeArt AI Eye Screening System"],
        "research_refs": [
            "EyeArt diabetic retinopathy screening",
            "EyeArt automated retinal analysis",
            "Eyenuk EyeArt",
            "EyeArt autonomous diabetic retinopathy",
        ],
        "company_names": ["Eyenuk", "Eyenuk Inc"],
        "legacy_names": [],
        "abbreviations": [],
    },

    "retinalscreen": {
        "fda_name": ["RetinalScreen"],
        "commercial_names": ["RetinalScreen", "Medios RetinalScreen"],
        "research_refs": [
            "RetinalScreen diabetic retinopathy",
            "Medios Technologies retinal screening",
        ],
        "company_names": [
            "Medios Technologies",
            "Medios Technologies Pte Ltd",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # CARDIAC
    # ======================================================================

    "caption guidance": {
        "fda_name": ["Caption Guidance"],
        "commercial_names": [
            "Caption Guidance",
            "Caption Health Guidance",
            "Caption AI Guidance",
        ],
        "research_refs": [
            "Caption Guidance echocardiography AI",
            "Caption Health AI-guided ultrasound",
            "AI-guided cardiac ultrasound Caption",
        ],
        "company_names": [
            "Caption Health",
            "Caption Health Inc",
            "GE HealthCare",
        ],
        "legacy_names": ["Bay Labs"],
        "abbreviations": [],
    },

    "caption interpretation": {
        "fda_name": ["Caption Interpretation"],
        "commercial_names": [
            "Caption Interpretation",
            "Caption Health Interpretation",
        ],
        "research_refs": [
            "Caption Interpretation ejection fraction",
            "Caption Health EF estimation",
            "AI echocardiogram interpretation Caption",
        ],
        "company_names": [
            "Caption Health",
            "Caption Health Inc",
            "GE HealthCare",
        ],
        "legacy_names": ["Bay Labs EchoMD"],
        "abbreviations": ["EF"],
    },

    "heartflow ffrct": {
        "fda_name": ["HeartFlow FFRCT Analysis"],
        "commercial_names": [
            "HeartFlow FFRct",
            "HeartFlow Analysis",
            "HeartFlow FFRCT",
        ],
        "research_refs": [
            "HeartFlow fractional flow reserve CT",
            "HeartFlow FFRct noninvasive",
            "CT-derived FFR HeartFlow",
            "HeartFlow coronary artery disease",
            "FFRCT analysis HeartFlow",
        ],
        "company_names": ["HeartFlow", "HeartFlow Inc"],
        "legacy_names": [],
        "abbreviations": ["FFRct", "FFRCT"],
    },

    "eko analysis software": {
        "fda_name": ["Eko Analysis Software"],
        "commercial_names": [
            "Eko Analysis Software",
            "Eko AI",
            "Eko Cardiac Screening",
        ],
        "research_refs": [
            "Eko AI murmur detection",
            "Eko cardiac screening algorithm",
            "Eko heart failure detection",
            "Eko low ejection fraction screening",
            "Eko digital stethoscope AI",
        ],
        "company_names": ["Eko", "Eko Health", "Eko Devices", "Eko Health Inc"],
        "legacy_names": [],
        "abbreviations": [],
    },

    "cardiologs": {
        "fda_name": ["Cardiologs ECG Analysis Platform"],
        "commercial_names": [
            "Cardiologs",
            "Cardiologs ECG Analysis",
            "Cardiologs Platform",
        ],
        "research_refs": [
            "Cardiologs ECG AI analysis",
            "Cardiologs atrial fibrillation detection",
            "Cardiologs arrhythmia detection",
            "Cardiologs deep learning ECG",
        ],
        "company_names": [
            "Cardiologs",
            "Cardiologs Technologies",
            "Cardiologs SAS",
            "Philips Cardiologs",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "viz aorto": {
        "fda_name": ["Viz Aorto"],
        "commercial_names": ["Viz Aorto", "Viz.ai Aorto"],
        "research_refs": [
            "Viz Aorto aortic emergency detection",
            "Viz.ai aortic dissection AI",
            "Viz Aorto type B dissection",
        ],
        "company_names": ["Viz.ai", "Viz.ai Inc"],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # RADIOLOGY — CANCER DETECTION
    # ======================================================================

    "paige prostate": {
        "fda_name": ["Paige Prostate"],
        "commercial_names": [
            "Paige Prostate",
            "Paige Prostate Alpha",
            "Paige.AI Prostate",
        ],
        "research_refs": [
            "Paige Prostate AI pathology",
            "Paige AI prostate cancer detection",
            "Paige prostate Gleason",
            "Paige digital pathology prostate",
        ],
        "company_names": [
            "Paige",
            "Paige AI",
            "Paige.AI",
            "Paige AI Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "saige-dx": {
        "fda_name": ["Saige-Dx"],
        "commercial_names": [
            "Saige-Dx",
            "Saige-Dx Mammography",
            "DeepHealth Saige-Dx",
        ],
        "research_refs": [
            "Saige-Dx breast cancer detection",
            "DeepHealth mammography AI",
            "Saige-Dx mammography triage",
        ],
        "company_names": [
            "DeepHealth",
            "DeepHealth Inc",
            "RadNet",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "transpara": {
        "fda_name": ["Transpara"],
        "commercial_names": [
            "Transpara",
            "ScreenPoint Transpara",
        ],
        "research_refs": [
            "Transpara mammography AI",
            "Transpara breast cancer screening",
            "ScreenPoint Medical Transpara",
            "Transpara AI mammography scoring",
        ],
        "company_names": [
            "ScreenPoint Medical",
            "ScreenPoint Medical BV",
            "ScreenPoint",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "profound ai": {
        "fda_name": ["ProFound AI"],
        "commercial_names": [
            "ProFound AI",
            "ProFound AI for Digital Breast Tomosynthesis",
            "ProFound AI for 2D Mammography",
            "iCAD ProFound AI",
        ],
        "research_refs": [
            "ProFound AI breast cancer detection",
            "iCAD ProFound AI mammography",
            "ProFound AI digital breast tomosynthesis",
            "ProFound AI DBT",
            "iCAD AI mammography",
        ],
        "company_names": [
            "iCAD",
            "iCAD Inc",
        ],
        "legacy_names": ["PowerLook"],
        "abbreviations": ["DBT"],
    },

    "lunit insight mmg": {
        "fda_name": ["Lunit INSIGHT MMG"],
        "commercial_names": [
            "Lunit INSIGHT MMG",
            "Lunit INSIGHT Mammography",
        ],
        "research_refs": [
            "Lunit INSIGHT MMG breast cancer",
            "Lunit mammography AI detection",
            "Lunit INSIGHT mammography screening",
        ],
        "company_names": [
            "Lunit",
            "Lunit Inc",
        ],
        "legacy_names": [],
        "abbreviations": ["MMG"],
    },

    "mammoscreen": {
        "fda_name": ["MammoScreen"],
        "commercial_names": [
            "MammoScreen",
            "Therapixel MammoScreen",
        ],
        "research_refs": [
            "MammoScreen breast cancer AI",
            "Therapixel MammoScreen mammography",
            "MammoScreen AI-assisted mammography",
        ],
        "company_names": [
            "Therapixel",
            "Therapixel SAS",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # RADIOLOGY — LUNG / CHEST
    # ======================================================================

    "lunit insight cxr": {
        "fda_name": ["Lunit INSIGHT CXR"],
        "commercial_names": [
            "Lunit INSIGHT CXR",
            "Lunit INSIGHT Chest X-ray",
        ],
        "research_refs": [
            "Lunit INSIGHT CXR chest radiograph",
            "Lunit AI chest x-ray",
            "Lunit INSIGHT lung nodule detection",
            "Lunit CXR tuberculosis screening",
        ],
        "company_names": [
            "Lunit",
            "Lunit Inc",
        ],
        "legacy_names": [],
        "abbreviations": ["CXR"],
    },

    "qxr": {
        "fda_name": ["qXR"],
        "commercial_names": [
            "qXR",
            "Qure.ai qXR",
        ],
        "research_refs": [
            "qXR chest x-ray AI",
            "Qure.ai qXR tuberculosis",
            "qXR automated chest radiograph",
            "Qure.ai chest x-ray interpretation",
        ],
        "company_names": [
            "Qure.ai",
            "Qure AI",
            "Qure.ai Technologies",
        ],
        "legacy_names": [],
        "abbreviations": ["CXR"],
    },

    "aidoc briefcase pe": {
        "fda_name": ["Aidoc BriefCase for Pulmonary Embolism"],
        "commercial_names": [
            "Aidoc BriefCase PE",
            "Aidoc PE",
            "BriefCase Pulmonary Embolism",
        ],
        "research_refs": [
            "Aidoc pulmonary embolism triage",
            "Aidoc BriefCase PE detection",
            "Aidoc AI pulmonary embolism CT",
        ],
        "company_names": ["Aidoc", "Aidoc Medical", "Aidoc Ltd"],
        "legacy_names": [],
        "abbreviations": ["PE"],
    },

    "riverain clearread ct": {
        "fda_name": ["ClearRead CT"],
        "commercial_names": [
            "ClearRead CT",
            "ClearRead CT Vessel Suppression",
            "ClearRead CT Detect",
            "Riverain ClearRead CT",
        ],
        "research_refs": [
            "ClearRead CT lung nodule detection",
            "Riverain ClearRead CT vessel suppression",
            "ClearRead CT bone suppression",
            "Riverain Technologies ClearRead",
        ],
        "company_names": [
            "Riverain Technologies",
            "Riverain Technologies LLC",
            "Riverain Medical",
        ],
        "legacy_names": ["SoftView"],
        "abbreviations": [],
    },

    # ======================================================================
    # RADIOLOGY — MSK / FRACTURE
    # ======================================================================

    "imagen osteodetect": {
        "fda_name": ["OsteoDetect"],
        "commercial_names": [
            "OsteoDetect",
            "Imagen OsteoDetect",
        ],
        "research_refs": [
            "OsteoDetect wrist fracture detection",
            "Imagen OsteoDetect distal radius fracture",
            "OsteoDetect AI fracture",
        ],
        "company_names": [
            "Imagen Technologies",
            "Imagen Technologies Inc",
            "Imagen",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "boneview": {
        "fda_name": ["BoneView"],
        "commercial_names": [
            "BoneView",
            "Gleamer BoneView",
        ],
        "research_refs": [
            "BoneView fracture detection AI",
            "Gleamer BoneView radiograph fracture",
            "BoneView AI-assisted fracture detection",
        ],
        "company_names": [
            "Gleamer",
            "Gleamer SAS",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "rayvolve": {
        "fda_name": ["RAYVOLVE"],
        "commercial_names": [
            "RAYVOLVE",
            "AZmed RAYVOLVE",
        ],
        "research_refs": [
            "RAYVOLVE fracture detection",
            "AZmed RAYVOLVE AI radiograph",
            "RAYVOLVE automated fracture",
        ],
        "company_names": [
            "AZmed",
            "AZ med",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # RADIOLOGY — IMAGE ENHANCEMENT
    # ======================================================================

    "air recon dl": {
        "fda_name": ["AIR Recon DL"],
        "commercial_names": [
            "AIR Recon DL",
            "GE AIR Recon DL",
        ],
        "research_refs": [
            "AIR Recon DL deep learning MRI reconstruction",
            "GE AIR Recon DL image quality",
            "AIR Recon DL noise reduction MRI",
        ],
        "company_names": [
            "GE Healthcare",
            "GE HealthCare",
            "General Electric Healthcare",
        ],
        "legacy_names": [],
        "abbreviations": ["DL"],
    },

    "subtlemr": {
        "fda_name": ["SubtleMR"],
        "commercial_names": [
            "SubtleMR",
            "Subtle Medical SubtleMR",
        ],
        "research_refs": [
            "SubtleMR MRI enhancement",
            "SubtleMR deep learning MRI",
            "Subtle Medical MRI noise reduction",
            "SubtleMR image quality improvement",
        ],
        "company_names": [
            "Subtle Medical",
            "Subtle Medical Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "subtlepet": {
        "fda_name": ["SubtlePET"],
        "commercial_names": [
            "SubtlePET",
            "Subtle Medical SubtlePET",
        ],
        "research_refs": [
            "SubtlePET PET image enhancement",
            "SubtlePET low-dose PET",
            "Subtle Medical PET deep learning",
            "SubtlePET dose reduction",
        ],
        "company_names": [
            "Subtle Medical",
            "Subtle Medical Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "aice": {
        "fda_name": ["Advanced intelligent Clear-IQ Engine"],
        "commercial_names": [
            "AiCE",
            "Advanced intelligent Clear-IQ Engine",
            "Canon AiCE",
        ],
        "research_refs": [
            "AiCE deep learning CT reconstruction",
            "Canon AiCE image reconstruction",
            "AiCE noise reduction CT",
            "Advanced intelligent Clear-IQ Engine CT",
        ],
        "company_names": [
            "Canon Medical Systems",
            "Canon Medical",
            "Canon Medical Systems Corporation",
        ],
        "legacy_names": [],
        "abbreviations": ["AiCE", "AICE"],
    },

    "true fidelity": {
        "fda_name": ["TrueFidelity"],
        "commercial_names": [
            "TrueFidelity",
            "True Fidelity",
            "GE TrueFidelity",
        ],
        "research_refs": [
            "TrueFidelity deep learning CT image reconstruction",
            "GE TrueFidelity CT reconstruction",
            "TrueFidelity noise reduction",
        ],
        "company_names": [
            "GE Healthcare",
            "GE HealthCare",
            "General Electric Healthcare",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "pixelshine": {
        "fda_name": ["PixelShine"],
        "commercial_names": [
            "PixelShine",
            "AlgoMedica PixelShine",
        ],
        "research_refs": [
            "PixelShine CT image enhancement",
            "PixelShine deep learning denoising",
            "AlgoMedica PixelShine CT noise reduction",
        ],
        "company_names": [
            "AlgoMedica",
            "AlgoMedica Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # GI / ENDOSCOPY
    # ======================================================================

    "gi genius": {
        "fda_name": ["GI Genius"],
        "commercial_names": [
            "GI Genius",
            "GI Genius Intelligent Endoscopy Module",
            "Medtronic GI Genius",
        ],
        "research_refs": [
            "GI Genius polyp detection",
            "GI Genius computer-aided detection colonoscopy",
            "GI Genius CADe colonoscopy",
            "Medtronic GI Genius adenoma detection",
            "Cosmo AI colonoscopy",
        ],
        "company_names": [
            "Medtronic",
            "Cosmo Pharmaceuticals",
            "Cosmo Intelligent Medical Devices",
            "Cosmo AI",
        ],
        "legacy_names": ["Cosmo Intelligent Medical Devices Discovery Module"],
        "abbreviations": ["CADe"],
    },

    "endobrain": {
        "fda_name": ["EndoBRAIN"],
        "commercial_names": [
            "EndoBRAIN",
            "EndoBRAIN-EYE",
            "EndoBRAIN-PLUS",
            "Cybernet EndoBRAIN",
        ],
        "research_refs": [
            "EndoBRAIN polyp characterization",
            "EndoBRAIN AI colonoscopy",
            "EndoBRAIN-EYE polyp detection",
            "Cybernet Systems EndoBRAIN",
        ],
        "company_names": [
            "Cybernet Systems",
            "Cybernet Systems Co Ltd",
            "Olympus (distributor)",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "skout": {
        "fda_name": ["SKOUT"],
        "commercial_names": [
            "SKOUT",
            "SKOUT Clinical Intelligence Engine",
            "Iterative Health SKOUT",
        ],
        "research_refs": [
            "SKOUT polyp detection endoscopy",
            "Iterative Health SKOUT colonoscopy",
            "SKOUT AI-assisted colonoscopy",
        ],
        "company_names": [
            "Iterative Health",
            "Iterative Health Inc",
            "Iterative Scopes",
        ],
        "legacy_names": ["Iterative Scopes"],
        "abbreviations": [],
    },

    # ======================================================================
    # DERMATOLOGY
    # ======================================================================

    "melafind": {
        "fda_name": ["MelaFind"],
        "commercial_names": [
            "MelaFind",
            "MELAFIND",
        ],
        "research_refs": [
            "MelaFind melanoma detection",
            "MelaFind multispectral imaging",
            "MELAFIND pigmented lesion analysis",
            "MelaFind skin cancer",
        ],
        "company_names": [
            "Strata Skin Sciences",
            "Strata Skin Sciences Inc",
            "MELA Sciences",
        ],
        "legacy_names": ["MELA Sciences MelaFind"],
        "abbreviations": [],
    },

    "dermasensor": {
        "fda_name": ["DermaSensor"],
        "commercial_names": [
            "DermaSensor",
        ],
        "research_refs": [
            "DermaSensor skin cancer detection",
            "DermaSensor elastic scattering spectroscopy",
            "DermaSensor AI skin lesion",
        ],
        "company_names": [
            "DermaSensor",
            "DermaSensor Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    # ======================================================================
    # SURGICAL
    # ======================================================================

    "mazor x": {
        "fda_name": ["Mazor X"],
        "commercial_names": [
            "Mazor X",
            "Mazor X Stealth Edition",
            "Mazor Robotics",
        ],
        "research_refs": [
            "Mazor X robotic spine surgery",
            "Mazor X Stealth spinal navigation",
            "Mazor robotics pedicle screw placement",
            "Mazor X surgical planning",
        ],
        "company_names": [
            "Medtronic",
            "Mazor Robotics",
            "Mazor Robotics Ltd",
        ],
        "legacy_names": [
            "Mazor Renaissance",
            "Mazor SpineAssist",
        ],
        "abbreviations": [],
    },

    "xvision spine": {
        "fda_name": ["xvision Spine System"],
        "commercial_names": [
            "xvision Spine",
            "xvision Spine System",
            "Augmedics xvision",
        ],
        "research_refs": [
            "xvision augmented reality spine surgery",
            "Augmedics xvision spinal navigation",
            "xvision AR surgical guidance",
        ],
        "company_names": [
            "Augmedics",
            "Augmedics Ltd",
        ],
        "legacy_names": [],
        "abbreviations": ["AR"],
    },

    # ======================================================================
    # ULTRASOUND
    # ======================================================================

    "caption health echo": {
        "fda_name": ["Caption Guidance"],
        "commercial_names": [
            "Caption Health",
            "Caption Guidance",
            "Caption AI",
        ],
        "research_refs": [
            "Caption Health AI-guided echocardiography",
            "Caption Guidance novice ultrasound",
            "Caption Health point-of-care echo",
        ],
        "company_names": [
            "Caption Health",
            "Caption Health Inc",
            "GE HealthCare",
        ],
        "legacy_names": ["Bay Labs"],
        "abbreviations": [],
    },

    "sonohealth": {
        "fda_name": ["SonoHealth"],
        "commercial_names": [
            "SonoHealth",
            "SonoHealth Vascular",
        ],
        "research_refs": [
            "SonoHealth ultrasound AI",
            "SonoHealth automated ultrasound analysis",
        ],
        "company_names": [
            "SonoHealth",
            "SonoHealth Inc",
        ],
        "legacy_names": [],
        "abbreviations": [],
    },

    "butterfly iq ai": {
        "fda_name": ["Butterfly iQ"],
        "commercial_names": [
            "Butterfly iQ",
            "Butterfly iQ+",
            "Butterfly iQ3",
            "Butterfly AI",
        ],
        "research_refs": [
            "Butterfly iQ AI ultrasound guidance",
            "Butterfly Network AI point-of-care ultrasound",
            "Butterfly iQ automated ejection fraction",
        ],
        "company_names": [
            "Butterfly Network",
            "Butterfly Network Inc",
        ],
        "legacy_names": ["Butterfly iQ"],
        "abbreviations": ["POCUS"],
    },

    # ======================================================================
    # PATHOLOGY
    # ======================================================================

    "proscia": {
        "fda_name": ["Concentriq Dx"],
        "commercial_names": [
            "Concentriq",
            "Concentriq Dx",
            "Proscia Concentriq",
            "Concentriq AP-Dx",
        ],
        "research_refs": [
            "Proscia digital pathology platform",
            "Concentriq digital pathology",
            "Proscia Concentriq AI pathology",
        ],
        "company_names": [
            "Proscia",
            "Proscia Inc",
        ],
        "legacy_names": ["Proscia"],
        "abbreviations": [],
    },

    # ======================================================================
    # ECG / CARDIAC MONITORING
    # ======================================================================

    "kardiamobile": {
        "fda_name": ["KardiaMobile"],
        "commercial_names": [
            "KardiaMobile",
            "KardiaMobile 6L",
            "KardiaMobile Card",
            "Kardia",
            "AliveCor KardiaMobile",
        ],
        "research_refs": [
            "KardiaMobile atrial fibrillation detection",
            "AliveCor KardiaMobile ECG",
            "KardiaMobile single-lead ECG",
            "AliveCor Kardia AI ECG",
            "KardiaMobile 6L six-lead ECG",
        ],
        "company_names": [
            "AliveCor",
            "AliveCor Inc",
        ],
        "legacy_names": ["AliveCor Heart Monitor"],
        "abbreviations": ["ECG", "AFib"],
    },

    "apple ecg": {
        "fda_name": ["Apple ECG App"],
        "commercial_names": [
            "Apple ECG",
            "Apple ECG App",
            "Apple Watch ECG",
            "ECG app on Apple Watch",
        ],
        "research_refs": [
            "Apple Watch ECG atrial fibrillation",
            "Apple Watch electrocardiogram",
            "Apple ECG app irregular rhythm notification",
            "Apple Watch single-lead ECG",
        ],
        "company_names": [
            "Apple",
            "Apple Inc",
        ],
        "legacy_names": [],
        "abbreviations": ["ECG", "AFib"],
    },

    "amps ecg": {
        "fda_name": ["AMPS ECG"],
        "commercial_names": [
            "AMPS ECG",
            "AMPS Algorithm",
        ],
        "research_refs": [
            "AMPS ECG algorithm",
            "AMPS AI ECG analysis",
        ],
        "company_names": [
            "Anumana",
            "Anumana Inc",
            "nference",
        ],
        "legacy_names": [],
        "abbreviations": ["ECG"],
    },
}


# ---------------------------------------------------------------------------
# Build a fast reverse-lookup index: lowered alias -> canonical key
# ---------------------------------------------------------------------------
_REVERSE_INDEX: Dict[str, str] = {}
for _key, _entry in DEVICE_ALIASES.items():
    for _field in (
        "fda_name",
        "commercial_names",
        "legacy_names",
        "abbreviations",
    ):
        for _alias in _entry.get(_field, []):
            _lc = _alias.strip().lower()
            if _lc not in _REVERSE_INDEX:
                _REVERSE_INDEX[_lc] = _key


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_aliases(device_name: str, company: Optional[str] = None) -> List[str]:
    """Return all known names / aliases for a device.

    Parameters
    ----------
    device_name : str
        Any recognisable name for the device (FDA name, brand name, etc.).
    company : str, optional
        Company name — used as a secondary lookup if device_name misses.

    Returns
    -------
    list[str]
        De-duplicated list of all names associated with the device.
    """
    key = _resolve_key(device_name, company)
    if key is None:
        return [device_name]  # fallback: just return what was given

    entry = DEVICE_ALIASES[key]
    seen: set[str] = set()
    aliases: list[str] = []
    for field in (
        "fda_name",
        "commercial_names",
        "research_refs",
        "company_names",
        "legacy_names",
    ):
        for val in entry.get(field, []):
            lc = val.lower()
            if lc not in seen:
                seen.add(lc)
                aliases.append(val)
    return aliases


def get_search_queries(
    device_name: str,
    company: Optional[str] = None,
    *,
    max_queries: int = 10,
) -> List[str]:
    """Generate a ranked list of PubMed / OpenAlex search queries for a device.

    The queries are ordered from most specific (exact product + company) to
    broadest (company-only fallback), which lets callers try narrow queries
    first and widen the net only when needed.

    Parameters
    ----------
    device_name : str
        Any recognisable name for the device.
    company : str, optional
        Company name — improves specificity.
    max_queries : int
        Cap on the number of queries returned (default 10).

    Returns
    -------
    list[str]
        Ordered search query strings ready for PubMed / OpenAlex.
    """
    key = _resolve_key(device_name, company)
    if key is None:
        # Fallback: generate basic queries from the raw inputs
        queries = [f'"{device_name}"']
        if company:
            queries.append(f'"{device_name}" AND "{company}"')
            queries.append(f'"{company}" AI')
        return queries[:max_queries]

    entry = DEVICE_ALIASES[key]
    queries: list[str] = []
    seen_lower: set[str] = set()

    def _add(q: str) -> None:
        lc = q.lower()
        if lc not in seen_lower:
            seen_lower.add(lc)
            queries.append(q)

    # --- Tier 1: exact FDA / commercial name + company ----------------------
    fda_names = entry.get("fda_name", [])
    commercial = entry.get("commercial_names", [])
    companies = entry.get("company_names", [])
    primary_company = companies[0] if companies else company

    for name in fda_names + commercial[:3]:
        _add(f'"{name}"')
        if primary_company:
            _add(f'"{name}" AND "{primary_company}"')

    # --- Tier 2: research-style references ----------------------------------
    for ref in entry.get("research_refs", [])[:4]:
        _add(f'"{ref}"')

    # --- Tier 3: legacy / rebranded names -----------------------------------
    for legacy in entry.get("legacy_names", []):
        _add(f'"{legacy}"')
        if primary_company:
            _add(f'"{legacy}" AND "{primary_company}"')

    # --- Tier 4: company-only fallback --------------------------------------
    if primary_company:
        _add(f'"{primary_company}" artificial intelligence')

    return queries[:max_queries]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_key(
    device_name: str, company: Optional[str] = None
) -> Optional[str]:
    """Find the canonical DEVICE_ALIASES key for a device name or company."""
    dn = device_name.strip().lower()

    # Direct key match
    if dn in DEVICE_ALIASES:
        return dn

    # Reverse-index match
    if dn in _REVERSE_INDEX:
        return _REVERSE_INDEX[dn]

    # Substring match (generous)
    for key in DEVICE_ALIASES:
        if dn in key or key in dn:
            return key

    # Try matching via company name
    if company:
        cl = company.strip().lower()
        for key, entry in DEVICE_ALIASES.items():
            for cn in entry.get("company_names", []):
                if cl in cn.lower() or cn.lower() in cl:
                    return key

    return None


# ---------------------------------------------------------------------------
# Quick smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Total devices catalogued: {len(DEVICE_ALIASES)}")
    print()

    # Demonstrate a few lookups
    test_cases = [
        ("IDx-DR", "Digital Diagnostics"),
        ("RAPID CTP", "iSchemaView"),
        ("HeartFlow FFRct", None),
        ("GI Genius", "Medtronic"),
        ("KardiaMobile", "AliveCor"),
        ("Paige Prostate", "Paige AI"),
        ("BoneView", "Gleamer"),
    ]
    for name, co in test_cases:
        print(f"--- {name} ({co or 'no company'}) ---")
        print("  Aliases:", get_aliases(name, co)[:5])
        print("  Queries:", get_search_queries(name, co, max_queries=4))
        print()

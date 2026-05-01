# VALIDMed

**Claims-Evidence Proportionality Audit for FDA AI/ML Medical Devices**

ValidMed analyzes the clinical claims and validation evidence in FDA 510(k) submissions for all 1,430 AI/ML-enabled medical devices. It extracts what each device claims to do and what evidence supports those claims, making the proportionality gap visible.

**Key finding:** 252 devices (19.5%) make high-impact clinical claims (detection, triage, diagnosis, treatment) backed only by bench testing or no validation data.

---

## The Problem

The FDA has cleared over 1,430 AI/ML-enabled medical devices. Most are cleared through the 510(k) pathway, which requires demonstration of substantial equivalence to a predicate device but does not mandate peer-reviewed clinical studies. There is no standardized way to assess whether the evidence in a device's submission is proportional to its clinical claims.

The April 2026 Nature Medicine editorial called for "proportional evidentiary standards" that "systematically and consistently link claims of impact to appropriate, proportional evidence." ValidMed operationalizes this call.

## What ValidMed Does

1. Downloads 510(k) summary PDFs from FDA AccessData for all 1,430 AI/ML devices
2. Extracts structured claims and validation evidence using LLM (Claude Haiku) + regex
3. Classifies each device's claim tier and evidence tier
4. Maps the proportionality gap in a searchable dashboard

## Findings

From analysis of 1,301 devices with available 510(k) PDFs:

| Claim Category | Devices | % |
|---|---|---|
| Quantification | 543 | 42% |
| Enhancement | 265 | 20% |
| Detection | 229 | 18% |
| Triage | 143 | 11% |
| Treatment | 58 | 4% |
| Diagnosis | 53 | 4% |

| Validation Design | Devices | % |
|---|---|---|
| Bench testing only | 851 | 65% |
| Retrospective multi-site | 226 | 17% |
| None reported | 108 | 8% |
| Prospective multi-site | 54 | 4% |
| Retrospective single-site | 34 | 3% |
| Prospective single-site | 25 | 2% |
| RCT | 3 | 0.2% |

- **252 devices (19.5%)** in the concern zone (high-impact claims + low-tier evidence)
- **60.4%** of diagnosis/treatment devices have only bench or no evidence
- **96.5%** of triage devices have no prospective data
- **Only 3 devices** report RCT-level evidence

---

## Data Sources

| Source | What it provides |
|---|---|
| FDA AI/ML Device List | Official catalog of 1,430 cleared devices |
| 510(k) Summary PDFs | Manufacturer-submitted claims, validation studies, performance metrics |
| openFDA MAUDE | Adverse event reports |
| openFDA Recalls | Device recall records |

## Methodology

### Claims Extraction

For each device with an available 510(k) PDF (1,301 of 1,430):

1. PDF text extracted using PyMuPDF
2. Claude Haiku extracts: intended use, claim category, validation design, performance metrics
3. Regex backstop catches metrics in longer documents
4. Each device classified on two axes: claim tier and evidence tier

### Claim Categories (increasing clinical impact)

- **Enhancement** -- image reconstruction, noise reduction, quality improvement
- **Quantification** -- automated measurements, volumetric analysis, scoring
- **Detection** -- flagging findings, identifying abnormalities, screening (CADe)
- **Triage** -- prioritizing worklists, routing urgent cases, notification (CADt)
- **Diagnosis** -- classifying conditions, autonomous diagnostic assessment (CADx)
- **Treatment** -- computing treatment parameters (radiation dose, surgical path)

### Evidence Tiers

- **None** -- no testing described
- **Bench only** -- algorithm tested on datasets (even if from multiple sources)
- **Retrospective single/multi** -- clinical study using retrospective patient data
- **Prospective single/multi** -- device tested on patients prospectively
- **RCT** -- randomized controlled trial

### Known Limitations

- 510(k) summaries vary in detail; absence of data does not mean no evidence exists in the full submission
- LLM extraction may misclassify claims or validation designs; all classifications should be verified against the linked PDF
- "Bench testing with multi-source data" is distinct from "multi-site clinical study" -- the prompt explicitly distinguishes these
- Safety data (MAUDE) depends on voluntary reporting
- No independent literature matching -- ValidMed analyzes manufacturer submissions, not published peer-reviewed studies

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+

### Pipeline

```bash
cd pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Copy .env.example to .env and add your API keys
cp .env.example .env

# Full pipeline (all sources, ~2-3 hours)
python run_full.py "data/ai-ml-enabled-devices-excel.xlsx"

# Extract claims from 510(k) PDFs (~30 min)
python extract_claims.py

# Build proportionality matrix
python proportionality_matrix.py
```

### Dashboard

```bash
cd web
npm install
npm run dev
```

---

## Tools

Code generation assisted by [Claude Code](https://claude.ai/code).

---

## License

MIT

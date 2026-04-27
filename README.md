# ValidMed

**Verified AI Literature & Intelligence Database for Medical Devices**

ValidMed is an open-source platform that systematically tracks the published evidence, safety record, and clinical trial activity for FDA-cleared AI/ML medical devices. It provides transparent, decomposable evidence scores to help hospitals, researchers, and policymakers make informed decisions about AI device adoption.

---

## The Problem

The FDA has cleared over 1,000 AI/ML-enabled medical devices, with new clearances accelerating each year. Yet there is no centralized, structured resource that links these devices to their post-market evidence base. Hospitals procure AI devices with limited visibility into whether a given product has been independently validated, involved in adverse events, or studied in prospective trials.

Existing resources (FDA databases, PubMed, MAUDE) are siloed. A clinician evaluating a new AI device must manually search across multiple databases, interpret regulatory filings, and assess study quality — a process that is time-consuming and often incomplete.

## What ValidMed Does

ValidMed automates this process across 1,430+ FDA-cleared AI/ML devices by:

1. Parsing the FDA's official AI/ML device list
2. Enriching each device with evidence from PubMed, Semantic Scholar, OpenFDA (MAUDE adverse events and recalls), and ClinicalTrials.gov
3. Computing a transparent 0-100 evidence score with visible component weights
4. Presenting results in a searchable, filterable dashboard

## Early Findings

Preliminary results from the full pipeline run (these numbers will be updated as methodology is refined):

- Approximately 50% of FDA-cleared AI/ML devices have zero indexed published evidence
- A minority of devices account for the majority of published validation studies
- Independent (non-manufacturer) validation remains uncommon for most devices
- Clinical trial registration is sparse relative to the number of cleared devices

These findings are descriptive and should be interpreted with the methodological caveats described below.

---

## Data Sources

| Source | What it provides |
|--------|-----------------|
| FDA AI/ML Device List | Canonical list of cleared devices, submission numbers, companies, specialty panels |
| PubMed (via NCBI E-utilities) | Published evidence — articles mentioning devices by name |
| Semantic Scholar | Additional publications not indexed in PubMed |
| OpenFDA / MAUDE | Adverse event reports and device recalls |
| ClinicalTrials.gov | Registered and completed clinical trials |

---

## Methodology

### Multi-Tier Search Strategy

Evidence retrieval uses a tiered approach to balance precision and recall:

- **Tier 1 (Direct):** Exact device name searched in PubMed title/abstract fields. High confidence — these are articles that explicitly name the device.
- **Tier 2 (Company + Device):** Company affiliation combined with device name. Catches publications where the device is referenced under alternative naming.
- **Tier 3 (Company + Specialty):** Company name combined with specialty-specific AI/ML keywords. Lower confidence, tagged as indirect. Post-filtered for relevance.

Each publication is tagged with its match tier so users can assess retrieval confidence.

### Evidence Scoring

Scores range from 0 to 100 and are fully decomposable:

| Component | Max Points | What it measures |
|-----------|-----------|-----------------|
| Evidence count | 40 | Number of indexed publications |
| Study quality | 20 | Highest-quality study type (RCT > clinical trial > meta-analysis > other) |
| Independence | 15 | Presence of non-manufacturer-authored studies |
| Safety record | 15 | Starts at 15, deductions for deaths, injuries, and recalls |
| Trial activity | 10 | Registered/completed trials, especially those with posted results |

### Known Limitations

- **Search sensitivity:** Devices with generic names (e.g., "CT") are excluded from name-based searches to avoid false positives. Some legitimate evidence may be missed for devices with ambiguous names.
- **Attribution:** PubMed searches match on device name strings. A publication mentioning a device name is not guaranteed to be a validation study of that specific device.
- **Temporal lag:** PubMed indexing and ClinicalTrials.gov updates lag behind actual publication and trial completion.
- **Score interpretation:** The evidence score reflects *quantity and type* of available evidence. It does not measure device efficacy or clinical utility. A low score means limited published evidence — not that a device is unsafe or ineffective.
- **MAUDE reporting:** Adverse event reports are voluntary and reflect reporting patterns, not true incidence rates.

---

## Tech Stack

- **Pipeline:** Python (httpx, openpyxl, supabase-py). Orchestrates multi-source enrichment with retry logic and checkpoint/resume support.
- **Database:** Supabase (PostgreSQL). Relational schema linking devices to evidence, safety events, recalls, and trials.
- **Dashboard:** React 18 + Vite. Lightweight client querying Supabase directly.

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project (free tier is sufficient)

### Pipeline Setup

```bash
cd pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `pipeline/config.py` with your API keys:

```python
NCBI_API_KEY = ""          # Optional, increases PubMed rate limits
PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_DELAY = 0.35        # Seconds between requests (respect NCBI rate limits)
SUPABASE_URL = ""          # Your Supabase project URL
SUPABASE_KEY = ""          # Your Supabase service role key
```

### Run the Pipeline

```bash
# Download the FDA AI/ML device list Excel file from:
# https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices

python run.py path/to/fda_device_list.xlsx

# Options:
#   --limit 50         Process only first N devices (for testing)
#   --upload           Upload results to Supabase after enrichment
#   --resume checkpoint.json   Resume from a previous checkpoint
```

### Database Setup

Apply the schema migration to your Supabase project:

```bash
supabase db push
# Or manually run: supabase/migrations/001_initial_schema.sql
```

### Web Dashboard

```bash
cd web
npm install
npm run dev
```

Create `web/.env` with:

```
VITE_SUPABASE_URL=your-project-url
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## Deploying to Vercel

1. Push the repo to GitHub
2. Import the project in [Vercel](https://vercel.com) and set the **Root Directory** to `web`
3. Vercel will auto-detect Vite. The build settings in `web/vercel.json` handle the rest:
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add environment variables in the Vercel dashboard:
   - `VITE_SUPABASE_URL` — your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY` — your Supabase anon/public key
5. Deploy. SPA routing and static data files in `public/data/` are served automatically.

---

## Contributing

Contributions are welcome. Priority areas:

- Improving search precision for devices with generic or ambiguous names
- Adding new enrichment sources (e.g., FDA 510(k) summary text analysis)
- Validating evidence scores against expert assessments
- Dashboard UX improvements

Please open an issue before starting significant work to discuss approach.

---

## Tools

Code generation assisted by [Claude Code](https://claude.ai/code).

---

## License

MIT

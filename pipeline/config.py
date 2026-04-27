import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY", "")

OPENFDA_BASE = "https://api.fda.gov"
PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CT_GOV_BASE = "https://clinicaltrials.gov/api/v2"

# Rate limit delays (seconds)
OPENFDA_DELAY = 0.3  # ~200 req/min with key
PUBMED_DELAY = 0.15  # ~7 req/sec with key
CT_GOV_DELAY = 0.2

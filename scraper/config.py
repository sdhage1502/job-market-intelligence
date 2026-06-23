# Configuration settings for Automated Job Market Platform

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Ensure data directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Connection (Supabase / Postgres)
# Check for environment variable SUPABASE_DB_URL, fallback to a local postgres URI if not provided
DB_URL = os.getenv("SUPABASE_DB_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

# Scraper Settings
# If MOCK_DATA_FALLBACK is True, or if the scraper encounters a 403/block, it will generate mock data.
MOCK_DATA_FALLBACK = os.getenv("MOCK_DATA_FALLBACK", "True").lower() in ("true", "1", "yes")

# Target Job Search Terms
JOB_ROLES = ["Data Analyst", "Data Engineer", "BI Analyst", "Analytics Engineer"]
CITIES = ["Bengaluru", "Pune", "Mumbai", "Hyderabad", "Delhi NCR", "Chennai", "Remote"]

# Scraping URLs (Indeed & Naukri search templates)
NAUKRI_URL_TEMPLATE = "https://www.naukri.com/{role}-jobs-in-{city}"
INDEED_URL_TEMPLATE = "https://in.indeed.com/jobs?q={role}&l={city}"

# HTTP Request Headers to simulate a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

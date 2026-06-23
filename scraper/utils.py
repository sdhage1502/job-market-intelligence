# Utility functions for Automated Job Market Platform Scraper

import hashlib
import logging
import sys

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("job-analytics-scraper")

def generate_job_hash(title: str, company: str, location: str, posted_date: str) -> str:
    """
    Generates a unique MD5 hash for a job posting to identify duplicates.
    Concatenates standardized title, company, location, and posted_date.
    """
    # Standardize strings (strip whitespace, convert to lowercase)
    s_title = str(title or "").strip().lower()
    s_company = str(company or "").strip().lower()
    s_location = str(location or "").strip().lower()
    s_posted = str(posted_date or "").strip().lower()
    
    combined = f"{s_title}|{s_company}|{s_location}|{s_posted}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

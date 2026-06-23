# Main Entry Point for Automated Job Market Analytics Scraper Pipeline

import json
import os
from datetime import datetime
from scraper.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from scraper.utils import logger
from scraper.extract import run_extraction
from scraper.transform import run_transformation
from scraper.load import load_jobs_to_db

def save_json_file(data: list, directory: str, filename_prefix: str) -> str:
    """Saves records as a JSON file in the target directory."""
    date_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"{filename_prefix}_{date_str}.json"
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved data snapshot: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving snapshot to {filepath}: {e}")
        raise e

def main():
    logger.info("==============================================")
    logger.info("Starting Automated Job Market Analytics ETL...")
    logger.info("==============================================")
    
    start_time = datetime.now()
    
    try:
        # Step 1: Extract raw data from job boards (or fallback mock generator)
        raw_jobs = run_extraction()
        save_json_file(raw_jobs, RAW_DATA_DIR, "jobs")
        
        # Step 2: Transform and clean raw postings
        cleaned_jobs = run_transformation(raw_jobs)
        save_json_file(cleaned_jobs, PROCESSED_DATA_DIR, "jobs_transformed")
        
        # Step 3: Load cleaned postings to Postgres/Supabase
        load_jobs_to_db(cleaned_jobs)
        
        duration = datetime.now() - start_time
        logger.info("==============================================")
        logger.info(f"ETL Pipeline successfully completed in {duration.total_seconds():.2f} seconds.")
        logger.info("==============================================")
        
    except Exception as e:
        logger.error("ETL Pipeline failed during execution:")
        logger.error(e, exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()

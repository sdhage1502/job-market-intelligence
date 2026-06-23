# Integration Test script for Automated Job Market Platform ETL Pipeline
# This script uses SQLite to mock PostgreSQL database operations to test the pipeline end-to-end

import sqlite3
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# Import scraper modules
from scraper.extract import run_extraction
from scraper.transform import run_transformation
from scraper.load import create_staging_table_if_not_exists

TEST_DIR = Path(__file__).resolve().parent / "test_snapshots"
TEST_RAW_DIR = TEST_DIR / "raw"
TEST_PROCESSED_DIR = TEST_DIR / "processed"

# Clean any existing test outputs
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_RAW_DIR.mkdir(parents=True, exist_ok=True)
TEST_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Helper to save JSON
def save_test_json(data: list, directory: Path, prefix: str):
    date_str = datetime.today().strftime("%Y-%m-%d")
    filepath = directory / f"{prefix}_{date_str}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filepath

def run_test_pipeline():
    print("====================================================")
    print("RUNNING END-TO-END PIPELINE INTEGRATION TEST (SQLITE)")
    print("====================================================")

    # 1. Extraction Test
    print("[1/4] Running extraction phase...")
    raw_jobs = run_extraction()
    assert len(raw_jobs) > 0, "Extraction failed: 0 jobs fetched."
    raw_filepath = save_test_json(raw_jobs, TEST_RAW_DIR, "jobs")
    print(f"Extraction successful. Snapshot saved: {raw_filepath} (Count: {len(raw_jobs)})")

    # 2. Transformation Test
    print("[2/4] Running transformation phase...")
    transformed_jobs = run_transformation(raw_jobs)
    assert len(transformed_jobs) > 0, "Transformation failed: 0 jobs transformed."
    assert len(transformed_jobs) <= len(raw_jobs), "Transformation shouldn't increase record counts."
    processed_filepath = save_test_json(transformed_jobs, TEST_PROCESSED_DIR, "jobs_transformed")
    print(f"Transformation successful. Snapshot saved: {processed_filepath} (Count: {len(transformed_jobs)})")
    
    # Verify hash constraints and clean locations
    first_job = transformed_jobs[0]
    assert "job_hash" in first_job, "Missing job_hash in transformed schema."
    assert len(first_job["job_hash"]) == 32, "Job hash should be 32-char MD5."
    assert "min_experience" in first_job, "Missing parsed experience fields."
    assert first_job["location"] in ["bengaluru", "pune", "mumbai", "hyderabad", "delhi ncr", "chennai", "remote"], "City normalization failed."

    # 3. Loading Test (Using SQLite to mock PostgreSQL schema)
    print("[3/4] Running loading phase into SQLite test database...")
    db_path = TEST_DIR / "test_jobs.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create SQLite staging table using equivalent syntax
    cur.execute("""
    CREATE TABLE IF NOT EXISTS staging_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_hash TEXT UNIQUE,
        title TEXT,
        company TEXT,
        location TEXT,
        salary_raw TEXT,
        experience_raw TEXT,
        skills_raw TEXT,
        description TEXT,
        source TEXT,
        posted_date TEXT,
        scraped_at TEXT
    );
    """)
    conn.commit()
    
    # Load into staging using SQLite INSERT OR REPLACE (equivalent to Postgres UPSERT)
    upsert_query = """
    INSERT OR REPLACE INTO staging_jobs (
        job_hash, title, company, location, salary_raw, 
        experience_raw, skills_raw, description, source, 
        posted_date, scraped_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    tuples_to_insert = [
        (
            job["job_hash"], job["title"], job["company"], job["location"], 
            job["salary_raw"], job["experience_raw"], job["skills_raw"], 
            job["description"], job["source"], job["posted_date"], job["scraped_at"]
        ) for job in transformed_jobs
    ]
    
    cur.executemany(upsert_query, tuples_to_insert)
    conn.commit()
    
    # Verify records in DB
    cur.execute("SELECT COUNT(*) FROM staging_jobs")
    inserted_count = cur.fetchone()[0]
    print(f"Loading successful. Inserted {inserted_count} jobs in test SQLite database.")
    assert inserted_count == len(transformed_jobs), f"Expected {len(transformed_jobs)} jobs, found {inserted_count}"

    # 4. Duplicate handling test (Re-run load to verify UPSERT constraints)
    print("[4/4] Verifying UPSERT duplicate handling...")
    # Insert the same batch again, check count stays the same
    cur.executemany(upsert_query, tuples_to_insert)
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM staging_jobs")
    post_upsert_count = cur.fetchone()[0]
    print(f"UPSERT duplicate count check: {post_upsert_count} jobs.")
    assert post_upsert_count == inserted_count, "Duplicate keys created new records instead of updating!"
    
    conn.close()
    
    # Clean up test directories
    shutil.rmtree(TEST_DIR)
    print("====================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! PIPELINE IS SOLID.")
    print("====================================================")

if __name__ == "__main__":
    run_test_pipeline()

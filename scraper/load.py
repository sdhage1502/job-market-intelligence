# Job Loading module for Automated Job Market Platform

import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any
from scraper.utils import logger
from scraper.config import DB_URL

def get_db_connection():
    """Establishes connection to PostgreSQL/Supabase database."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database at {DB_URL.split('@')[-1]}: {e}")
        raise e

def create_staging_table_if_not_exists(conn) -> None:
    """Creates the raw staging table if it doesn't already exist in the database."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS staging_jobs (
        id SERIAL PRIMARY KEY,
        job_hash TEXT UNIQUE,
        title TEXT,
        company TEXT,
        location TEXT,
        salary_raw TEXT,
        experience_raw TEXT,
        skills_raw TEXT,
        description TEXT,
        source TEXT,
        posted_date DATE,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_staging_jobs_hash ON staging_jobs(job_hash);
    CREATE INDEX IF NOT EXISTS idx_staging_jobs_posted_date ON staging_jobs(posted_date);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            conn.commit()
            logger.info("Staging table verification completed.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating staging table: {e}")
        raise e

def load_jobs_to_db(jobs: List[Dict[str, Any]]) -> int:
    """
    Upserts job records into PostgreSQL staging table.
    Uses UPSERT logic (ON CONFLICT DO UPDATE).
    """
    if not jobs:
        logger.info("No jobs to load.")
        return 0
        
    conn = None
    records_loaded = 0
    
    try:
        conn = get_db_connection()
        create_staging_table_if_not_exists(conn)
        
        insert_query = """
        INSERT INTO staging_jobs (
            job_hash, title, company, location, salary_raw, 
            experience_raw, skills_raw, description, source, 
            posted_date, scraped_at
        ) VALUES %s
        ON CONFLICT (job_hash) DO UPDATE SET
            title = EXCLUDED.title,
            company = EXCLUDED.company,
            location = EXCLUDED.location,
            salary_raw = EXCLUDED.salary_raw,
            experience_raw = EXCLUDED.experience_raw,
            skills_raw = EXCLUDED.skills_raw,
            description = EXCLUDED.description,
            source = EXCLUDED.source,
            scraped_at = EXCLUDED.scraped_at;
        """
        
        # Format jobs into tuple list for execute_values
        data_tuples = []
        for job in jobs:
            data_tuples.append((
                job["job_hash"],
                job["title"],
                job["company"],
                job["location"],
                job["salary_raw"],
                job["experience_raw"],
                job["skills_raw"],
                job["description"],
                job["source"],
                job["posted_date"],
                job["scraped_at"]
            ))
            
        with conn.cursor() as cur:
            execute_values(cur, insert_query, data_tuples)
            conn.commit()
            records_loaded = len(jobs)
            logger.info(f"Successfully upserted {records_loaded} records to the staging database.")
            
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error loading jobs to staging database: {e}")
        raise e
    finally:
        if conn:
            conn.close()
            
    return records_loaded

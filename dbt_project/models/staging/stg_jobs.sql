-- Staging model to clean and cast raw columns from staging_jobs ingestion table

WITH raw_jobs AS (
    SELECT * FROM {{ source('raw_data', 'staging_jobs') }}
)

SELECT
    id AS staging_id,
    job_hash,
    title AS job_title,
    company AS company_name,
    location AS city,
    salary_raw,
    experience_raw,
    skills_raw,
    description AS job_description,
    source,
    COALESCE(posted_date, CURRENT_DATE)::DATE AS posted_date,
    COALESCE(scraped_at, CURRENT_TIMESTAMP)::TIMESTAMP AS scraped_at
FROM raw_jobs

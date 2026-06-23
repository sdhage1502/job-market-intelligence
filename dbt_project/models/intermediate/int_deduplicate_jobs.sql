-- Intermediate model to deduplicate staging job records by job_hash using ROW_NUMBER()

WITH ranked_jobs AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY job_hash 
            ORDER BY scraped_at DESC
        ) as row_num
    FROM {{ ref('stg_jobs') }}
)

SELECT
    staging_id,
    job_hash,
    job_title,
    company_name,
    city,
    salary_raw,
    experience_raw,
    skills_raw,
    job_description,
    source,
    posted_date,
    scraped_at
FROM ranked_jobs
WHERE row_num = 1

-- Central Fact Table linking all Dimension tables in Star Schema

WITH jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
)

SELECT
    MD5(job_hash) AS job_key,
    job_hash,
    MD5(company_name) AS company_key,
    MD5(city || '_' || (CASE WHEN city = 'remote' THEN 'true' ELSE 'false' END)) AS location_key,
    -- Convert date format to YYYYMMDD integer for dim_date join
    TO_CHAR(posted_date, 'YYYYMMDD')::INT AS date_key,
    MD5(salary_raw) AS salary_key,
    1 AS posting_count
FROM jobs

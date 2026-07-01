-- Staging model to extract distinct locations from raw staging_jobs table

WITH raw_jobs AS (
    SELECT * FROM {{ source('raw_data', 'staging_jobs') }}
)

SELECT DISTINCT
    TRIM(LOWER(location)) AS city,
    CASE WHEN TRIM(LOWER(location)) = 'remote' THEN TRUE ELSE FALSE END AS is_remote
FROM raw_jobs
WHERE location IS NOT NULL AND TRIM(location) != ''

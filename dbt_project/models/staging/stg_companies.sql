-- Staging model to extract distinct companies from raw staging_jobs table

WITH raw_jobs AS (
    SELECT * FROM {{ source('raw_data', 'staging_jobs') }}
)

SELECT DISTINCT
    TRIM(company) AS company_name,
    -- Placeholder industry classification (enriched in marts layer)
    'Unknown' AS industry
FROM raw_jobs
WHERE company IS NOT NULL AND TRIM(company) != ''

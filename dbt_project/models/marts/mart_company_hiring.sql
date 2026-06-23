-- Mart model aggregating job postings by company and industry

WITH jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
),

companies AS (
    SELECT *
    FROM {{ ref('dim_company') }}
)

SELECT
    c.company_name,
    c.industry,
    j.posted_date,
    COUNT(*) AS posting_count
FROM jobs j
JOIN companies c ON MD5(j.company_name) = c.company_key
GROUP BY 1, 2, 3

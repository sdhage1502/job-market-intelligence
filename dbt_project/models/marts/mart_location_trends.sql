-- Mart model aggregating job postings count by city and remote work configurations

WITH jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
),

locations AS (
    SELECT *
    FROM {{ ref('dim_location') }}
)

SELECT
    l.city,
    l.state,
    l.country,
    l.is_remote,
    j.posted_date,
    COUNT(*) AS posting_count
FROM jobs j
JOIN locations l ON MD5(j.city || '_' || (CASE WHEN j.city = 'remote' THEN 'true' ELSE 'false' END)) = l.location_key
GROUP BY 1, 2, 3, 4, 5

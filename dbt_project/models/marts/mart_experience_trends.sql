-- Mart model for experience analytics (Dashboard Page 5)
-- Categorizes jobs into experience brackets and computes salary correlations
-- Uses: CTEs, CASE, Window Functions (RANK), Joins

WITH jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
),

salaries AS (
    SELECT *
    FROM {{ ref('dim_salary') }}
),

experience_parsed AS (
    SELECT
        j.job_hash,
        j.job_title,
        j.company_name,
        j.city,
        j.experience_raw,
        j.posted_date,
        s.avg_salary,
        s.min_salary,
        s.max_salary,
        -- Parse min experience from the raw text
        CASE
            WHEN j.experience_raw ~ '(\d+)\s*[-–]\s*(\d+)'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)\s*[-–]\s*(\d+)'))[1]::INT
            WHEN j.experience_raw ~ '(\d+)\s*\+'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)\s*\+'))[1]::INT
            WHEN j.experience_raw ~ '(\d+)'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)'))[1]::INT
            ELSE NULL
        END AS min_exp,
        -- Parse max experience from the raw text
        CASE
            WHEN j.experience_raw ~ '(\d+)\s*[-–]\s*(\d+)'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)\s*[-–]\s*(\d+)'))[2]::INT
            WHEN j.experience_raw ~ '(\d+)\s*\+'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)\s*\+'))[1]::INT + 5
            WHEN j.experience_raw ~ '(\d+)'
                THEN (REGEXP_MATCH(j.experience_raw, '(\d+)'))[1]::INT
            ELSE NULL
        END AS max_exp
    FROM jobs j
    LEFT JOIN salaries s ON MD5(j.salary_raw) = s.salary_key
),

bracketed AS (
    SELECT
        *,
        CASE
            WHEN min_exp IS NULL THEN 'Not Specified'
            WHEN min_exp <= 2 THEN '0-2 years (Entry)'
            WHEN min_exp <= 5 THEN '2-5 years (Junior)'
            WHEN min_exp <= 8 THEN '5-8 years (Mid-Senior)'
            ELSE '8+ years (Lead/Principal)'
        END AS experience_bracket,
        -- Numeric sort order for bracket
        CASE
            WHEN min_exp IS NULL THEN 99
            WHEN min_exp <= 2 THEN 1
            WHEN min_exp <= 5 THEN 2
            WHEN min_exp <= 8 THEN 3
            ELSE 4
        END AS bracket_sort_order
    FROM experience_parsed
)

SELECT
    experience_bracket,
    bracket_sort_order,
    job_title,
    company_name,
    city,
    posted_date,
    EXTRACT(MONTH FROM posted_date)::INT AS month,
    EXTRACT(YEAR FROM posted_date)::INT AS year,
    min_exp,
    max_exp,
    avg_salary,
    COUNT(*) AS posting_count,
    AVG(avg_salary) AS avg_salary_for_bracket,
    RANK() OVER (
        PARTITION BY experience_bracket
        ORDER BY COUNT(*) DESC
    ) AS bracket_demand_rank
FROM bracketed
WHERE experience_bracket != 'Not Specified'
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11

-- Mart model benchmarking average salary statistics by role, company, and city

WITH jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
),

salaries AS (
    SELECT *
    FROM {{ ref('dim_salary') }}
)

SELECT
    j.job_title,
    j.company_name,
    j.city,
    j.posted_date,
    AVG(s.min_salary) AS avg_min_salary,
    AVG(s.max_salary) AS avg_max_salary,
    AVG(s.avg_salary) AS avg_avg_salary,
    COUNT(*) AS posting_count
FROM jobs j
JOIN salaries s ON MD5(j.salary_raw) = s.salary_key
WHERE s.avg_salary > 0.0 -- Filter out undisclosed salaries for active benchmarks
GROUP BY 1, 2, 3, 4

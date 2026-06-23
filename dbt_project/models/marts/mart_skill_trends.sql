-- Mart view/table summarizing skill demand frequency over time

WITH exploded_skills AS (
    SELECT *
    FROM {{ ref('int_skills_exploded') }}
),

jobs AS (
    SELECT *
    FROM {{ ref('int_deduplicate_jobs') }}
)

SELECT
    s.skill_name,
    s.skill_category,
    j.posted_date,
    EXTRACT(MONTH FROM j.posted_date)::INT AS month,
    EXTRACT(YEAR FROM j.posted_date)::INT AS year,
    COUNT(*) AS skill_frequency
FROM exploded_skills s
JOIN jobs j ON s.job_hash = j.job_hash
GROUP BY 1, 2, 3, 4, 5

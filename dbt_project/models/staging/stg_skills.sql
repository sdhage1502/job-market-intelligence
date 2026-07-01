-- Staging model to extract individual skills from raw staging_jobs comma-separated skills_raw field

WITH raw_jobs AS (
    SELECT * FROM {{ source('raw_data', 'staging_jobs') }}
),

split_skills AS (
    SELECT
        job_hash,
        TRIM(UNNEST(STRING_TO_ARRAY(skills_raw, ','))) AS skill_name
    FROM raw_jobs
    WHERE skills_raw IS NOT NULL AND TRIM(skills_raw) != ''
)

SELECT DISTINCT
    LOWER(TRIM(skill_name)) AS skill_name
FROM split_skills
WHERE TRIM(skill_name) != ''

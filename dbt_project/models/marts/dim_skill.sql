-- Skill Dimension Model

WITH unique_skills AS (
    SELECT DISTINCT 
        skill_name,
        skill_category
    FROM {{ ref('int_skills_exploded') }}
    WHERE skill_name IS NOT NULL AND TRIM(skill_name) != ''
)

SELECT
    -- MD5-based surrogate key for unique skill matching
    MD5(skill_name) AS skill_key,
    skill_name,
    skill_category
FROM unique_skills

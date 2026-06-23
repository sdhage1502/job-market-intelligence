-- Intermediate model to split comma-separated skills list into separate rows with categories

WITH split_skills AS (
    SELECT 
        job_hash,
        TRIM(UNNEST(STRING_TO_ARRAY(skills_raw, ','))) AS skill_name
    FROM {{ ref('int_deduplicate_jobs') }}
    WHERE skills_raw IS NOT NULL AND TRIM(skills_raw) != ''
)

SELECT DISTINCT
    job_hash,
    LOWER(skill_name) AS skill_name,
    CASE 
        WHEN LOWER(skill_name) IN ('python', 'r', 'scala', 'java', 'javascript', 'c++', 'julia') THEN 'Programming'
        WHEN LOWER(skill_name) IN ('sql', 'postgresql', 'mysql', 'oracle', 'sql server', 'pl/sql') THEN 'Database'
        WHEN LOWER(skill_name) IN ('power bi', 'tableau', 'excel', 'looker', 'metabase', 'qlik', 'google data studio', 'reporting') THEN 'BI & Visualization'
        WHEN LOWER(skill_name) IN ('dbt', 'airflow', 'spark', 'hadoop', 'kafka', 'nifi', 'talend', 'pentaho') THEN 'Data Engineering'
        WHEN LOWER(skill_name) IN ('aws', 'azure', 'gcp', 'snowflake', 'databricks', 'redshift', 'bigquery', 'cloud') THEN 'Cloud Infrastructure'
        WHEN LOWER(skill_name) IN ('docker', 'kubernetes', 'git', 'jenkins', 'ci/cd', 'github actions') THEN 'DevOps'
        ELSE 'General'
    END AS skill_category
FROM split_skills
WHERE TRIM(skill_name) != ''

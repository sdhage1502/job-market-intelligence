-- Location Dimension Model

WITH unique_locations AS (
    SELECT DISTINCT 
        city,
        CASE WHEN city = 'remote' THEN TRUE ELSE FALSE END AS is_remote
    FROM {{ ref('int_deduplicate_jobs') }}
    WHERE city IS NOT NULL AND TRIM(city) != ''
)

SELECT
    -- MD5 surrogate key linking location metrics
    MD5(city || '_' || (CASE WHEN is_remote THEN 'true' ELSE 'false' END)) AS location_key,
    city,
    CASE 
        WHEN city = 'pune' THEN 'Maharashtra'
        WHEN city = 'mumbai' THEN 'Maharashtra'
        WHEN city = 'bengaluru' THEN 'Karnataka'
        WHEN city = 'hyderabad' THEN 'Telangana'
        WHEN city = 'delhi ncr' THEN 'Delhi'
        WHEN city = 'chennai' THEN 'Tamil Nadu'
        ELSE 'Remote'
    END AS state,
    CASE WHEN city = 'remote' THEN 'Global' ELSE 'India' END AS country,
    is_remote
FROM unique_locations

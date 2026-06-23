-- Salary Dimension Model
-- Parses numeric salary bounds from raw text using PostgreSQL regular expressions

WITH raw_salaries AS (
    SELECT DISTINCT 
        salary_raw
    FROM {{ ref('int_deduplicate_jobs') }}
    WHERE salary_raw IS NOT NULL
),

parsed_salaries AS (
    SELECT
        salary_raw,
        -- Remove everything except digits and dashes to leave only e.g. '400000-600000'
        CASE 
            WHEN salary_raw IN ('Not Disclosed', '') THEN 0.0
            ELSE 
                COALESCE(
                    NULLIF(
                        SPLIT_PART(
                            REGEXP_REPLACE(salary_raw, '[^\d\-]', '', 'g'), 
                            '-', 
                            1
                        ), 
                        ''
                    )::NUMERIC, 
                    0.0
                )
        END AS min_salary_parsed,
        
        CASE 
            WHEN salary_raw IN ('Not Disclosed', '') THEN 0.0
            ELSE 
                COALESCE(
                    NULLIF(
                        SPLIT_PART(
                            REGEXP_REPLACE(salary_raw, '[^\d\-]', '', 'g'), 
                            '-', 
                            2
                        ), 
                        ''
                    )::NUMERIC, 
                    COALESCE(
                        NULLIF(
                            SPLIT_PART(
                                REGEXP_REPLACE(salary_raw, '[^\d\-]', '', 'g'), 
                                '-', 
                                1
                            ), 
                            ''
                        )::NUMERIC, 
                        0.0
                    )
                )
        END AS max_salary_parsed
    FROM raw_salaries
)

SELECT
    MD5(salary_raw) AS salary_key,
    salary_raw,
    min_salary_parsed AS min_salary,
    max_salary_parsed AS max_salary,
    ((min_salary_parsed + max_salary_parsed) / 2.0) AS avg_salary,
    'INR' AS currency
FROM parsed_salaries

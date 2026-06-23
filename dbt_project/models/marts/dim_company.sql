-- Company Dimension Model

WITH unique_companies AS (
    SELECT DISTINCT company_name
    FROM {{ ref('int_deduplicate_jobs') }}
    WHERE company_name IS NOT NULL AND TRIM(company_name) != ''
)

SELECT
    -- MD5-based surrogate key for unique company mapping
    MD5(company_name) AS company_key,
    company_name,
    CASE 
        WHEN company_name IN ('Google', 'Microsoft', 'Amazon', 'Meta', 'Netflix', 'Snowflake', 'Stripe') THEN 'Technology'
        WHEN company_name IN ('TCS', 'Infosys', 'Wipro', 'Cognizant', 'Capgemini', 'L&T Infotech') THEN 'IT Services'
        WHEN company_name IN ('Deloitte', 'PwC', 'Accenture') THEN 'Consulting'
        WHEN company_name IN ('Razorpay', 'CRED', 'PhonePe') THEN 'Fintech'
        WHEN company_name IN ('Swiggy', 'Zomato', 'Flipkart') THEN 'E-commerce & Logistics'
        ELSE 'Technology'
    END AS industry
FROM unique_companies

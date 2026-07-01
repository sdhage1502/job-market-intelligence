-- ============================================================================
-- Analytics SQL Queries for the Automated Job Market Analytics Platform
-- Run these directly against the completed Star Schema & Mart tables
-- Required SQL techniques: CTEs, Window Functions, LAG(), RANK(), ROW_NUMBER(), Joins
-- ============================================================================


-- ============================================================================
-- 1. TOP IN-DEMAND SKILLS
-- ============================================================================

SELECT 
    skill_name, 
    skill_category,
    SUM(skill_frequency) AS demand_frequency
FROM mart_skill_trends
GROUP BY skill_name, skill_category
ORDER BY demand_frequency DESC
LIMIT 15;


-- ============================================================================
-- 2. MONTH-OVER-MONTH (MoM) SKILL DEMAND GROWTH — uses LAG()
-- ============================================================================

WITH monthly_skills AS (
    SELECT 
        skill_name,
        skill_category,
        month,
        year,
        SUM(skill_frequency) AS total_demand
    FROM mart_skill_trends
    GROUP BY 1, 2, 3, 4
),

lagged_data AS (
    SELECT 
        skill_name,
        skill_category,
        month,
        year,
        total_demand,
        LAG(total_demand, 1, 0) OVER (
            PARTITION BY skill_name 
            ORDER BY year, month
        ) AS prev_month_demand
    FROM monthly_skills
)

SELECT 
    skill_name,
    skill_category,
    month,
    year,
    total_demand,
    prev_month_demand,
    CASE 
        WHEN prev_month_demand = 0 THEN 0.0
        ELSE ROUND(((total_demand - prev_month_demand)::NUMERIC / prev_month_demand) * 100, 2)
    END AS growth_rate_pct
FROM lagged_data
ORDER BY year DESC, month DESC, growth_rate_pct DESC;


-- ============================================================================
-- 3. AVERAGE BENCHMARK SALARY (INR)
-- ============================================================================

SELECT 
    ROUND(AVG(avg_salary), 2) AS average_salary_inr,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY avg_salary), 2) AS median_salary_inr,
    ROUND(MIN(min_salary), 2) AS minimum_salary_inr,
    ROUND(MAX(max_salary), 2) AS maximum_salary_inr
FROM dim_salary
WHERE avg_salary > 0;


-- ============================================================================
-- 4. TOP HIRING CITIES — uses COUNT, GROUP BY, RANK()
-- ============================================================================

WITH city_postings AS (
    SELECT 
        city,
        state,
        is_remote,
        SUM(posting_count) AS total_postings
    FROM mart_location_trends
    GROUP BY 1, 2, 3
)

SELECT 
    city,
    state,
    is_remote,
    total_postings,
    RANK() OVER (ORDER BY total_postings DESC) AS city_rank
FROM city_postings
ORDER BY city_rank;


-- ============================================================================
-- 5. TOP HIRING COMPANIES — uses RANK() and JOIN
-- ============================================================================

WITH company_postings AS (
    SELECT 
        company_name,
        industry,
        SUM(posting_count) AS total_postings
    FROM mart_company_hiring
    GROUP BY 1, 2
)

SELECT 
    company_name,
    industry,
    total_postings,
    RANK() OVER (ORDER BY total_postings DESC) AS company_rank
FROM company_postings
ORDER BY company_rank
LIMIT 20;


-- ============================================================================
-- 6. SALARY BY ROLE AND CITY — uses CTEs and JOINs
-- ============================================================================

SELECT 
    job_title,
    city,
    ROUND(AVG(avg_avg_salary), 2) AS avg_salary,
    ROUND(MAX(avg_max_salary), 2) AS max_salary,
    SUM(posting_count) AS total_postings
FROM mart_salary_trends
WHERE avg_avg_salary > 0
GROUP BY 1, 2
ORDER BY avg_salary DESC;


-- ============================================================================
-- 7. REMOTE vs ON-SITE HIRING RATIO
-- ============================================================================

WITH remote_stats AS (
    SELECT
        is_remote,
        SUM(posting_count) AS total_postings
    FROM mart_location_trends
    GROUP BY is_remote
)

SELECT 
    CASE WHEN is_remote THEN 'Remote' ELSE 'On-site' END AS work_type,
    total_postings,
    ROUND(total_postings * 100.0 / SUM(total_postings) OVER (), 2) AS percentage
FROM remote_stats;


-- ============================================================================
-- 8. FASTEST GROWING SKILLS (MoM) — uses LAG() and ROW_NUMBER()
-- ============================================================================

WITH monthly_skills AS (
    SELECT 
        skill_name,
        month,
        year,
        SUM(skill_frequency) AS total_demand
    FROM mart_skill_trends
    GROUP BY 1, 2, 3
),

growth_calc AS (
    SELECT 
        skill_name,
        month,
        year,
        total_demand,
        LAG(total_demand, 1, 0) OVER (
            PARTITION BY skill_name 
            ORDER BY year, month
        ) AS prev_demand,
        CASE 
            WHEN LAG(total_demand, 1, 0) OVER (PARTITION BY skill_name ORDER BY year, month) = 0 THEN 0
            ELSE ROUND(
                ((total_demand - LAG(total_demand, 1, 0) OVER (PARTITION BY skill_name ORDER BY year, month))::NUMERIC 
                / LAG(total_demand, 1, 0) OVER (PARTITION BY skill_name ORDER BY year, month)) * 100, 2
            )
        END AS growth_pct
    FROM monthly_skills
),

ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY growth_pct DESC) AS growth_rank
    FROM growth_calc
    WHERE growth_pct > 0
)

SELECT * FROM ranked WHERE growth_rank <= 10;


-- ============================================================================
-- 9. EXPERIENCE BRACKET DISTRIBUTION
-- ============================================================================

SELECT
    experience_bracket,
    SUM(posting_count) AS total_postings,
    ROUND(AVG(avg_salary_for_bracket), 2) AS avg_salary_for_bracket,
    ROUND(SUM(posting_count) * 100.0 / SUM(SUM(posting_count)) OVER (), 2) AS bracket_percentage
FROM mart_experience_trends
GROUP BY experience_bracket, bracket_sort_order
ORDER BY bracket_sort_order;


-- ============================================================================
-- 10. ENTRY-LEVEL JOB PERCENTAGE (KPI)
-- ============================================================================

WITH total AS (
    SELECT SUM(posting_count) AS total_jobs FROM mart_experience_trends
),

entry AS (
    SELECT SUM(posting_count) AS entry_jobs 
    FROM mart_experience_trends 
    WHERE experience_bracket = '0-2 years (Entry)'
)

SELECT 
    entry_jobs,
    total_jobs,
    ROUND(entry_jobs * 100.0 / NULLIF(total_jobs, 0), 2) AS entry_level_percentage
FROM entry, total;

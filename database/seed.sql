-- Seed data for Automated Job Market Analytics Platform
-- Targets: PostgreSQL (Supabase / Local)

-- 1. Seed dim_date for years 2025 to 2030
INSERT INTO dim_date (date_key, full_date, month, quarter, year)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d::DATE AS full_date,
    EXTRACT(MONTH FROM d)::INT AS month,
    EXTRACT(QUARTER FROM d)::INT AS quarter,
    EXTRACT(YEAR FROM d)::INT AS year
FROM generate_series('2025-01-01'::DATE, '2030-12-31'::DATE, '1 day'::INTERVAL) d
ON CONFLICT (date_key) DO NOTHING;

-- 2. Seed some common skills and their categories
INSERT INTO dim_skill (skill_name, skill_category) VALUES
('python', 'Programming'),
('sql', 'Database'),
('power bi', 'BI & Visualization'),
('tableau', 'BI & Visualization'),
('excel', 'BI & Visualization'),
('dbt', 'Data Engineering'),
('aws', 'Cloud Infrastructure'),
('azure', 'Cloud Infrastructure'),
('gcp', 'Cloud Infrastructure'),
('spark', 'Big Data'),
('hadoop', 'Big Data'),
('scala', 'Programming'),
('java', 'Programming'),
('javascript', 'Programming'),
('git', 'DevOps'),
('docker', 'DevOps'),
('kubernetes', 'DevOps'),
('airflow', 'Data Engineering'),
('snowflake', 'Database'),
('postgresql', 'Database')
ON CONFLICT (skill_name) DO NOTHING;

-- 3. Seed some default companies
INSERT INTO dim_company (company_name, industry) VALUES
('Google', 'Technology'),
('Microsoft', 'Technology'),
('Amazon', 'E-commerce / Technology'),
('Meta', 'Social Media'),
('Netflix', 'Streaming / Tech'),
('Tata Consultancy Services', 'IT Services'),
('Infosys', 'IT Services'),
('Wipro', 'IT Services'),
('Cognizant', 'IT Services'),
('Accenture', 'Management Consulting / IT')
ON CONFLICT (company_name) DO NOTHING;

-- Create schema script for Automated Job Market Analytics Platform
-- Targets: PostgreSQL (Supabase / Local)

-- 1. Ingestion / Staging Table
CREATE TABLE IF NOT EXISTS staging_jobs (
    id SERIAL PRIMARY KEY,
    job_hash TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    salary_raw TEXT,
    experience_raw TEXT,
    skills_raw TEXT,
    description TEXT,
    source TEXT,
    posted_date DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on hash and posted date for staging table performance
CREATE INDEX IF NOT EXISTS idx_staging_jobs_hash ON staging_jobs(job_hash);
CREATE INDEX IF NOT EXISTS idx_staging_jobs_posted_date ON staging_jobs(posted_date);

-- 2. Star Schema Dimension Tables

-- Company Dimension
CREATE TABLE IF NOT EXISTS dim_company (
    company_key SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL UNIQUE,
    industry TEXT DEFAULT 'Tech'
);

-- Location Dimension
CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    state TEXT,
    country TEXT DEFAULT 'India',
    is_remote BOOLEAN DEFAULT FALSE,
    UNIQUE(city, state, country, is_remote)
);

-- Skill Dimension
CREATE TABLE IF NOT EXISTS dim_skill (
    skill_key SERIAL PRIMARY KEY,
    skill_name TEXT NOT NULL UNIQUE,
    skill_category TEXT DEFAULT 'General'
);

-- Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY, -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    month INT NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL
);

-- Salary Dimension
CREATE TABLE IF NOT EXISTS dim_salary (
    salary_key SERIAL PRIMARY KEY,
    min_salary NUMERIC(12, 2) DEFAULT 0.0,
    max_salary NUMERIC(12, 2) DEFAULT 0.0,
    avg_salary NUMERIC(12, 2) DEFAULT 0.0,
    currency TEXT DEFAULT 'INR',
    UNIQUE(min_salary, max_salary, avg_salary, currency)
);

-- 3. Star Schema Fact Table
CREATE TABLE IF NOT EXISTS fact_jobs (
    job_key SERIAL PRIMARY KEY,
    job_hash TEXT NOT NULL UNIQUE,
    company_key INT REFERENCES dim_company(company_key),
    location_key INT REFERENCES dim_location(location_key),
    date_key INT REFERENCES dim_date(date_key),
    salary_key INT REFERENCES dim_salary(salary_key),
    posting_count INT DEFAULT 1
);

-- Indexes for Fact Table
CREATE INDEX IF NOT EXISTS idx_fact_jobs_company ON fact_jobs(company_key);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_location ON fact_jobs(location_key);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_date ON fact_jobs(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_salary ON fact_jobs(salary_key);

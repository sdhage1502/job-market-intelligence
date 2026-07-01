# Automated Job Market Platform & Power BI Pipeline (2026)

An automated end-to-end data analytics engineering platform that scrapes job listings daily, stores raw and transformed data in a PostgreSQL Data Warehouse, designs a Star Schema using dbt (Data Build Tool) Core, and visualizes market insights using Power BI.

---

## 🏗️ Architecture

```text
  Job Boards (Indeed/Naukri)
              │
              ▼
    Python Scraper (ETL) ──► Saves snapshot raw JSON (/data/raw/)
              │
              ▼
   Transformed JSON snapshot (/data/processed/)
              │
              ▼
  Supabase / PostgreSQL [public.staging_jobs]
              │
              ▼
      dbt Core Pipeline 
    ┌─────────┴─────────┐
    │  staging views    │ (stg_jobs)
    ├───────────────────┤
    │  intermediate     │ (int_deduplicate_jobs, int_skills_exploded)
    ├───────────────────┤
    │  marts (tables)   │ (dim_company, dim_location, dim_skill, dim_date, dim_salary, fact_jobs)
    └─────────┬─────────┘
              ▼
   Power BI Desktop / Dashboard Layers
```

---

## 🛠️ Technology Stack

* **Data Extraction**: Python 3.12, BeautifulSoup4, Requests (polite scraping with browser-agent emulation)
* **Resilience fallback**: Integrated Mock Market Generator (guarantees run success inside server environments/CI)
* **Database**: PostgreSQL (Supabase hosted)
* **Transformation**: dbt Core (Staging ➔ Ephemeral/View ➔ Table Star Schema marts)
* **Containerization**: Docker (Multi-stage build)
* **CI/CD**: GitHub Actions (Nightly execution schedule, database schema migrations, and snapshot auto-commits)
* **BI Visuals**: Power BI Desktop

---

## 📂 Project Structure

```text
automated-job-market-platform/
│── scraper/
│   │── __init__.py
│   │── main.py            # Main entry point coordinating ETL flow
│   │── config.py          # App configuration, selector maps, and credentials
│   │── extract.py         # HTTP fetcher, scraper parse functions, mock generator fallback
│   │── transform.py       # Data cleaning, experience parsing, city normalization
│   │── load.py            # PostgreSQL staging connection and UPSERT loader
│   │── utils.py           # Logging, hashing, file handling
│
│── data/
│   │── raw/               # Snapshot database raw JSON outputs
│   │── processed/         # Structured cleaned JSON records
│
│── database/
│   │── schema.sql             # SQL schema definitions for staging, dimensions, and facts
│   │── seed.sql               # Initial database seeds (dim_date, dim_skill, dim_company)
│   │── analytics_queries.sql  # 10 production SQL analytics queries (LAG, RANK, ROW_NUMBER, CTEs)
│
│── dbt_project/               # dbt Core project directory
│   │── dbt_project.yml        # dbt configuration file
│   │── profiles.yml           # dbt connection profiles (PostgreSQL)
│   │── models/
│   │   │── staging/           # Cast types & base schemas (stg_jobs, stg_companies, stg_locations, stg_skills)
│   │   │── intermediate/      # Deduplication and unnest parsing (int_deduplicate_jobs, int_skills_exploded)
│   │   │── marts/             # Dimensions, facts, and analytical trends (dim_*, fact_jobs, mart_*)
│
│── docker/
│   │── Dockerfile             # Docker recipe for execution container
│
│── powerbi/
│   │── README.md              # DAX calculations, schema layout, visual configuration (5 pages)
│
│── .github/
│   │── workflows/
│   │   │── pipeline.yml       # Daily scheduled run (scraper, dbt run, verification)
│
│── docker-compose.yml         # Local dev: PostgreSQL + ETL + dbt in one command
│── .gitignore                 # Standard Python/dbt/Docker ignore rules
│── requirements.txt           # Dependencies
│── test_pipeline.py           # End-to-end integration test (SQLite mock)
└── README.md                  # Documentation
```

---

## 🚀 Getting Started

### 1. Pre-requisites & Local Setup

Clone the repository and install dependencies in a python virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a local `.env` file or export variables to set connection parameters:

```env
# Database Credentials
SUPABASE_DB_URL="postgresql://postgres:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

# Scraper Settings
MOCK_DATA_FALLBACK="True"  # Toggle to "False" to run live web crawling

# dbt Credentials (mapped from DB_URL)
DBT_HOST="aws-0-ap-south-1.pooler.supabase.com"
DBT_USER="postgres"
DBT_PASSWORD="[PASSWORD]"
DBT_PORT="5432"
DBT_ENV_DB="postgres"
```

### 3. Initialize Database Schema & Seed Data

Ensure database tables and calendar dimension seeds are created:

```bash
# Connect to your Postgres and run:
psql -d $SUPABASE_DB_URL -f database/schema.sql
psql -d $SUPABASE_DB_URL -f database/seed.sql
```

### 4. Run Python ETL Pipeline

Run extraction, processing, local snapshots creation, and staging upsert:

```bash
python scraper/main.py
```

### 5. Run dbt Transformation Layer

Compile and run the dbt models to build/refresh the Star Schema:

```bash
cd dbt_project
dbt run
dbt test
```

---

## 🚢 Dockerized Run

### Option A: Docker Compose (Recommended for Local Dev)

Spin up PostgreSQL + run the full ETL + dbt pipeline in one command:

```bash
docker-compose up --build
```

This will:
1. Start a local PostgreSQL 16 instance with auto-initialized schema & seed data
2. Run the Python ETL pipeline (extract → transform → load)
3. Execute `dbt run` and `dbt test` against the warehouse

To tear down:
```bash
docker-compose down -v
```

### Option B: Standalone Docker (Production / CI)

```bash
docker build -f docker/Dockerfile -t job-analytics-etl .
docker run --env-file .env job-analytics-etl
```

---

## 📊 SQL Analytics Queries

The following analytical queries run directly against the completed Star Schema and marts:

### 1. Top In-Demand Skills
```sql
SELECT 
    skill_name, 
    SUM(skill_frequency) AS demand_frequency
FROM mart_skill_trends
GROUP BY skill_name
ORDER BY demand_frequency DESC
LIMIT 10;
```

### 2. Month-over-Month (MoM) Skill Demand Growth (using LAG)
```sql
WITH monthly_skills AS (
    SELECT 
        skill_name,
        month,
        year,
        SUM(skill_frequency) AS total_demand
    FROM mart_skill_trends
    GROUP BY 1, 2, 3
),
lagged_data AS (
    SELECT 
        skill_name,
        month,
        year,
        total_demand,
        LAG(total_demand, 1, 0) OVER (PARTITION BY skill_name ORDER BY year, month) AS prev_month_demand
    FROM monthly_skills
)
SELECT 
    skill_name,
    month,
    year,
    total_demand,
    prev_month_demand,
    CASE 
        WHEN prev_month_demand = 0 THEN 0.0
        ELSE ROUND(((total_demand - prev_month_demand)::NUMERIC / prev_month_demand) * 100, 2)
    END AS growth_rate_pct
FROM lagged_data
ORDER BY growth_rate_pct DESC;
```

### 3. Average Benchmark Salary (INR)
```sql
SELECT 
    ROUND(AVG(avg_salary), 2) AS average_salary_inr,
    ROUND(MIN(min_salary), 2) AS minimum_salary_inr,
    ROUND(MAX(max_salary), 2) AS maximum_salary_inr
FROM dim_salary
WHERE avg_salary > 0;
```

### 4. Top Hiring Cities
```sql
SELECT 
    city, 
    SUM(posting_count) AS job_postings_count,
    ROUND(AVG(CASE WHEN is_remote THEN 1 ELSE 0 END) * 100, 2) AS remote_jobs_percentage
FROM mart_location_trends
GROUP BY city
ORDER BY job_postings_count DESC;
```

### 5. Top Hiring Companies (using RANK)
```sql
WITH company_postings AS (
    SELECT 
        company_name, industry,
        SUM(posting_count) AS total_postings
    FROM mart_company_hiring
    GROUP BY 1, 2
)
SELECT 
    company_name, industry, total_postings,
    RANK() OVER (ORDER BY total_postings DESC) AS company_rank
FROM company_postings
ORDER BY company_rank
LIMIT 20;
```

### 6. Experience Bracket Distribution
```sql
SELECT
    experience_bracket,
    SUM(posting_count) AS total_postings,
    ROUND(AVG(avg_salary_for_bracket), 2) AS avg_salary_for_bracket,
    ROUND(SUM(posting_count) * 100.0 / SUM(SUM(posting_count)) OVER (), 2) AS bracket_percentage
FROM mart_experience_trends
GROUP BY experience_bracket, bracket_sort_order
ORDER BY bracket_sort_order;
```

> **📁 Full Query Set**: See [`database/analytics_queries.sql`](database/analytics_queries.sql) for all 10 production SQL analytics queries.

---

## 📈 KPIs Tracked

| KPI | Source |
|-----|--------|
| Total Jobs Scraped | `fact_jobs` |
| Average Salary | `dim_salary` |
| Top Hiring Company | `mart_company_hiring` |
| Top Hiring City | `mart_location_trends` |
| Most Demanded Skill | `mart_skill_trends` |
| Fastest Growing Skill | `mart_skill_trends` + LAG() |
| Remote Hiring % | `dim_location` |
| Entry-Level Job % | `mart_experience_trends` |

---

## 🧪 Testing

Run the end-to-end integration test (uses SQLite as mock database):

```bash
python test_pipeline.py
```

This validates:
1. Extraction generates records (mock fallback)
2. Transformation cleans data, normalizes cities, generates hashes
3. Loading with UPSERT deduplication works correctly
4. Hash uniqueness constraints are enforced

# Automated Job Market Platform & Power BI Pipeline (2026)

## Project Goal

Build a fully automated end-to-end analytics platform that scrapes job listings daily, stores raw and transformed data in PostgreSQL, models the data using a Star Schema, transforms it using dbt, and visualizes insights in Power BI.

This project should demonstrate:

* Data scraping automation
* ETL pipeline design
* Data warehouse modeling
* SQL analytics
* dbt transformations
* Business intelligence dashboards
* DevOps automation

This project should look like a real-world analytics engineering pipeline.

---

# Core Business Problem

Job seekers and analysts lack real-time structured insights into:

* Which skills are most in demand
* Which roles pay highest
* Which cities are hiring most
* What hiring trends are growing month-over-month
* Which technologies are becoming more valuable

The platform should automate this.

---

# Tech Stack

## Data Collection

* Python 3.12
* Requests
* BeautifulSoup4
* Selenium (fallback)
* lxml

---

## Database

* PostgreSQL
* Supabase (hosted PostgreSQL)

---

## Transformation

* dbt Core

---

## Containerization

* Docker

---

## BI Layer

* Power BI Desktop

---

## Automation

* GitHub Actions

---

# Architecture

```text
Job Boards
   ↓
Python Scraper
   ↓
Raw JSON Files
   ↓
Supabase PostgreSQL (staging)
   ↓
dbt Transformation Layer
   ↓
Analytics Warehouse (Star Schema)
   ↓
Power BI Dashboard
   ↓
Daily Scheduled GitHub Actions
```

---

# Project Folder Structure

```bash
job-market-analytics/
│── scraper/
│   │── main.py
│   │── config.py
│   │── extract.py
│   │── transform.py
│   │── load.py
│   │── utils.py
│
│── data/
│   │── raw/
│   │── processed/
│
│── database/
│   │── schema.sql
│   │── seed.sql
│
│── dbt_project/
│   │── models/
│   │   │── staging/
│   │   │── intermediate/
│   │   │── marts/
│   │── dbt_project.yml
│
│── docker/
│   │── Dockerfile
│
│── powerbi/
│   │── dashboards.pbix
│
│── .github/
│   │── workflows/
│   │   │── pipeline.yml
│
│── requirements.txt
│── README.md
```

---

# Step 1: Scraper Requirements

Target sources:

* Naukri
* Indeed

Scrape fields:

```text
job_id
job_title
company_name
location
salary
experience_required
job_description
skills
job_type
posted_date
source
scraped_at
```

Rules:

* Create unique hash for every record
* Remove broken entries
* Handle missing salary values
* Normalize city names
* Parse experience into integer range

Hash logic:

```python
hash(title + company + location + posted_date)
```

Save output:

```text
/data/raw/jobs_YYYY_MM_DD.json
```

---

# Step 2: Python ETL Flow

## extract.py

Responsibilities:

* Fetch HTML
* Parse job cards
* Extract metadata

Functions:

```python
fetch_jobs()
parse_job_cards()
extract_skills()
```

---

## transform.py

Responsibilities:

Clean:

* salary formatting
* skill splitting
* remove duplicate spaces
* lowercase standardization
* null replacements

Normalize:

```text
Pune → pune
Mumbai → mumbai
Bangalore → bengaluru
```

Convert:

```text
3-5 years → min_exp=3 max_exp=5
```

---

## load.py

Responsibilities:

Insert data into PostgreSQL staging table.

Table:

```sql
staging_jobs
```

Use UPSERT logic.

---

# Step 3: PostgreSQL Database Design

Use Star Schema.

---

## staging_jobs

Raw ingestion table.

Columns:

```sql
id SERIAL PRIMARY KEY
job_hash TEXT UNIQUE
title TEXT
company TEXT
location TEXT
salary_raw TEXT
experience_raw TEXT
skills_raw TEXT
description TEXT
source TEXT
posted_date DATE
scraped_at TIMESTAMP
```

---

# Dimension Tables

---

## dim_company

```sql
company_key SERIAL PRIMARY KEY
company_name TEXT
industry TEXT
```

---

## dim_location

```sql
location_key SERIAL PRIMARY KEY
city TEXT
state TEXT
country TEXT
is_remote BOOLEAN
```

---

## dim_skill

```sql
skill_key SERIAL PRIMARY KEY
skill_name TEXT
skill_category TEXT
```

Examples:

* SQL
* Python
* Power BI
* Tableau
* Excel
* dbt
* AWS

---

## dim_date

```sql
date_key SERIAL PRIMARY KEY
full_date DATE
month INT
quarter INT
year INT
```

---

## dim_salary

```sql
salary_key SERIAL PRIMARY KEY
min_salary NUMERIC
max_salary NUMERIC
avg_salary NUMERIC
currency TEXT
```

---

# Fact Table

## fact_jobs

```sql
job_key SERIAL PRIMARY KEY
company_key INT
location_key INT
date_key INT
salary_key INT
posting_count INT
```

Relationship:

```text
fact_jobs → all dimensions
```

---

# Step 4: dbt Models

Create 3 layers.

---

## Staging Layer

models/staging/

Files:

```text
stg_jobs.sql
stg_companies.sql
stg_locations.sql
stg_skills.sql
```

Tasks:

* clean raw fields
* cast datatypes
* split salary
* split experience

---

## Intermediate Layer

models/intermediate/

Files:

```text
int_deduplicate_jobs.sql
int_skills_exploded.sql
```

Tasks:

Deduplicate:

Use:

```sql
ROW_NUMBER() OVER (
PARTITION BY job_hash ORDER BY scraped_at DESC
)
```

Skill explode:

Convert:

```text
Python, SQL, Power BI
```

Into:

```text
Python
SQL
Power BI
```

---

## Mart Layer

models/marts/

Files:

```text
mart_skill_trends.sql
mart_salary_trends.sql
mart_location_trends.sql
mart_company_hiring.sql
```

---

# Analytics Queries

---

## Top Skills

```sql
SELECT skill_name, COUNT(*)
FROM mart_skill_trends
GROUP BY skill_name
ORDER BY COUNT(*) DESC;
```

---

## Month-over-Month Skill Growth

Use:

```sql
WITH monthly_skills AS (
   ...
),
lagged_data AS (
   ...
)
SELECT *
FROM lagged_data;
```

Use:

```sql
LAG()
```

Required.

---

## Average Salary

```sql
SELECT AVG(avg_salary)
FROM dim_salary;
```

---

## Top Hiring Cities

```sql
SELECT city, COUNT(*)
FROM mart_location_trends
GROUP BY city
ORDER BY COUNT(*) DESC;
```

---

# Step 5: Docker Setup

Create Dockerfile:

```dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "scraper/main.py"]
```

Requirements:

Container must:

* run scraper
* save JSON
* load DB

---

# Step 6: GitHub Actions Automation

File:

```text
.github/workflows/pipeline.yml
```

Schedule:

```yaml
cron: '0 1 * * *'
```

Runs nightly.

Workflow:

1. Checkout repo
2. Build Docker image
3. Run scraper
4. Push raw data
5. Load Supabase
6. Run dbt models

Secrets:

```text
SUPABASE_DB_URL
DBT_PROFILES_DIR
```

Required.

---

# Step 7: Power BI Dashboard Requirements

Create 5 dashboard pages.

---

## Page 1: Executive Overview

KPIs:

* Total Jobs
* Avg Salary
* Top Skill
* Top City
* Remote Jobs %

Charts:

* Hiring trend line
* Salary distribution
* Job growth

---

## Page 2: Skill Trends

Charts:

* Top skills
* MoM growth
* Skill demand heatmap

DAX:

```DAX
Skill Growth % =
DIVIDE(
Current Month - Previous Month,
Previous Month
)
```

---

## Page 3: Salary Analytics

Charts:

* Salary by role
* Salary by city
* Salary by company

Metrics:

* Average
* Median
* Highest

---

## Page 4: Location Analytics

Charts:

* Hiring by city
* Remote vs onsite
* City demand ranking

Map required.

---

## Page 5: Experience Analytics

Charts:

* 0–2 years
* 2–5 years
* 5–8 years
* 8+ years

Distribution chart.

---

# KPIs to Track

```text
Total jobs scraped
Average salary
Top hiring company
Top hiring city
Most demanded skill
Fastest growing skill
Remote hiring %
Entry-level job %
```

---

# Important Rules

Must use:

* CTEs
* Window Functions
* Joins
* LAG()
* RANK()
* ROW_NUMBER()

Must implement:

* deduplication logic
* data normalization
* star schema
* dbt lineage
* nightly automation

---

# Resume Output Goal

Final result must justify:

"Built an automated job market analytics pipeline using Python, PostgreSQL, dbt, Docker, GitHub Actions, and Power BI to analyze hiring trends, salary benchmarks, and skill demand with daily automated data refreshes."

This exact level of complexity is required.

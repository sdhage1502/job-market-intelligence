# Job Extraction module for Automated Job Market Platform

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from scraper.utils import logger
from scraper.config import HEADERS, MOCK_DATA_FALLBACK, JOB_ROLES, CITIES

def fetch_html(url: str) -> str:
    """Fetches HTML content from a URL with retry logic."""
    for attempt in range(3):
        try:
            time.sleep(random.uniform(1.0, 3.0)) # Polite delay
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
    return ""

def scrape_naukri(role: str, city: str) -> List[Dict[str, Any]]:
    """
    Attempts to scrape Naukri search page.
    Note: Naukri heavily uses JS and dynamic loading (API requests).
    This function parses the server-rendered HTML skeleton or falls back to mock.
    """
    url = f"https://www.naukri.com/{role.lower().replace(' ', '-')}-jobs-in-{city.lower()}"
    logger.info(f"Attempting to scrape Naukri: {url}")
    html = fetch_html(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    jobs = []
    
    # Selectors for job cards on Naukri (often modern pages rely on JS, so fallback is active)
    cards = soup.select(".srp-jobtuple, .jobTuple")
    for card in cards:
        try:
            title_el = card.select_one("a.title, .title")
            company_el = card.select_one("a.subTitle, .subTitle")
            loc_el = card.select_one(".location, .locWdth")
            sal_el = card.select_one(".salary, .salWdth")
            exp_el = card.select_one(".experience, .expWdth")
            skills_el = card.select(".tags, .tagGrp li")
            desc_el = card.select_one(".job-description, .desc")
            
            title = title_el.text.strip() if title_el else ""
            company = company_el.text.strip() if company_el else ""
            location = loc_el.text.strip() if loc_el else city
            salary = sal_el.text.strip() if sal_el else ""
            experience = exp_el.text.strip() if exp_el else ""
            skills = ", ".join([s.text.strip() for s in skills_el]) if skills_el else ""
            description = desc_el.text.strip() if desc_el else ""
            job_id = card.get("data-job-id", str(random.randint(100000, 999999)))
            
            jobs.append({
                "job_id": job_id,
                "job_title": title,
                "company_name": company,
                "location": location,
                "salary": salary,
                "experience_required": experience,
                "job_description": description,
                "skills": skills,
                "job_type": "Full-time",
                "posted_date": datetime.today().strftime("%Y-%m-%d"),
                "source": "Naukri",
                "scraped_at": datetime.now().isoformat()
            })
        except Exception as e:
            logger.debug(f"Error parsing Naukri job card: {e}")
            
    return jobs

def scrape_indeed(role: str, city: str) -> List[Dict[str, Any]]:
    """Attempts to scrape Indeed search results."""
    url = f"https://in.indeed.com/jobs?q={role}&l={city}"
    logger.info(f"Attempting to scrape Indeed: {url}")
    html = fetch_html(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    jobs = []
    
    cards = soup.select(".job_seen_beacon, .result")
    for card in cards:
        try:
            title_el = card.select_one("h2.jobTitle, .jobTitle span")
            company_el = card.select_one(".companyName, [data-testid='company-name']")
            loc_el = card.select_one(".companyLocation, [data-testid='text-location']")
            sal_el = card.select_one(".salary-snippet-container, .metadata.salarySnippet")
            exp_el = card.select_one(".attribute_snippet") # simplified
            desc_el = card.select_one(".job-snippet, .jobCardReqContainer")
            
            title = title_el.text.strip() if title_el else ""
            company = company_el.text.strip() if company_el else ""
            location = loc_el.text.strip() if loc_el else city
            salary = sal_el.text.strip() if sal_el else ""
            experience = exp_el.text.strip() if exp_el and "year" in exp_el.text.lower() else ""
            description = desc_el.text.strip() if desc_el else ""
            job_id = card.get("data-jk", str(random.randint(100000, 999999)))
            
            jobs.append({
                "job_id": job_id,
                "job_title": title,
                "company_name": company,
                "location": location,
                "salary": salary,
                "experience_required": experience,
                "job_description": description,
                "skills": "", # Indeed rarely lists tags in the list view
                "job_type": "Full-time",
                "posted_date": datetime.today().strftime("%Y-%m-%d"),
                "source": "Indeed",
                "scraped_at": datetime.now().isoformat()
            })
        except Exception as e:
            logger.debug(f"Error parsing Indeed job card: {e}")
            
    return jobs

def generate_mock_jobs(count: int = 50) -> List[Dict[str, Any]]:
    """Generates highly realistic job market postings for testing & CI runs."""
    logger.info(f"Generating {count} mock job postings for testing and fallback mode...")
    
    companies = [
        "Google", "Microsoft", "Amazon", "Meta", "Netflix", "TCS", "Infosys", "Wipro",
        "Cognizant", "Accenture", "Deloitte", "PwC", "Flipkart", "Razorpay", "CRED",
        "PhonePe", "Capgemini", "L&T Infotech", "Swiggy", "Zomato", "Stripe", "Snowflake"
    ]
    
    industries = {
        "Google": "Technology", "Microsoft": "Technology", "Amazon": "E-commerce",
        "Meta": "Social Media", "Netflix": "Entertainment", "TCS": "IT Services",
        "Infosys": "IT Services", "Wipro": "IT Services", "Cognizant": "IT Services",
        "Accenture": "IT Services", "Deloitte": "Consulting", "PwC": "Consulting",
        "Flipkart": "E-commerce", "Razorpay": "Fintech", "CRED": "Fintech",
        "PhonePe": "Fintech", "Capgemini": "IT Services", "L&T Infotech": "IT Services",
        "Swiggy": "Logistics / Tech", "Zomato": "Logistics / Tech", "Stripe": "Fintech",
        "Snowflake": "Technology"
    }

    job_titles_map = {
        "Data Analyst": ["Data Analyst", "Junior Data Analyst", "Senior Data Analyst", "Business Data Analyst", "Data Analytics Lead"],
        "Data Engineer": ["Data Engineer", "Senior Data Engineer", "Lead Data Engineer", "Big Data Engineer", "Cloud Data Engineer"],
        "BI Analyst": ["BI Analyst", "Business Intelligence Developer", "Power BI Engineer", "Tableau Analytics Specialist"],
        "Analytics Engineer": ["Analytics Engineer", "Senior Analytics Engineer", "dbt Analytics Developer", "Data Platform Engineer"]
    }
    
    skills_pool = {
        "Data Analyst": ["SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics", "R", "SAS"],
        "Data Engineer": ["SQL", "Python", "AWS", "Spark", "Airflow", "Docker", "Kubernetes", "Scala", "Java", "Snowflake", "dbt", "Kafka"],
        "BI Analyst": ["Power BI", "Tableau", "SQL", "Excel", "Data Modeling", "DAX", "SSIS", "SSAS", "SQL Server"],
        "Analytics Engineer": ["SQL", "dbt", "Snowflake", "Python", "Airflow", "PostgreSQL", "Git", "Docker", "Looker", "BigQuery"]
    }

    salaries_pool = [
        "₹ 4,00,000 - 6,00,000 P.A.", "₹ 6,00,000 - 9,00,000 P.A.", "₹ 10,00,000 - 15,00,000 P.A.",
        "₹ 15,00,000 - 25,00,000 P.A.", "₹ 25,00,000 - 40,00,000 P.A.", "Not Disclosed", "Competitive Salary",
        "₹ 8,00,000 - 12,00,000 P.A.", "₹ 12,00,000 - 18,00,000 P.A."
    ]

    experiences_pool = [
        "0-2 years", "1-3 years", "2-5 years", "3-5 Yrs", "5-8 years", "8-10 years",
        "4-7 Yrs", "2-4 years", "6-9 Yrs"
    ]
    
    descriptions_pool = [
        "We are looking for a candidate who is passionate about building scalable data architectures, pipeline orchestration, and transforming raw records to support business analytical solutions.",
        "The ideal candidate will write complex SQL scripts, build dashboards, translate requirements to metric logic, and conduct regular deep-dives on user growth and performance metric dashboards.",
        "Join our tech team to coordinate daily extraction routines, optimize databases, enforce constraints, design star schemas, and build semantic data models using dbt and Power BI dashboards.",
        "You will design, develop, and maintain secure and scalable ELT/ETL pipelines, build clean reporting layers, work with stakeholders to define core metrics, and perform root cause analysis on data issues."
    ]

    mock_jobs = []
    
    # Generate records spread over the past 30 days
    today = datetime.today()
    
    for i in range(count):
        role = random.choice(JOB_ROLES)
        city = random.choice(CITIES)
        company = random.choice(companies)
        title = random.choice(job_titles_map[role])
        
        # Select 3-6 random skills for this role
        job_skills = random.sample(skills_pool[role], k=random.randint(3, 6))
        skills_str = ", ".join(job_skills)
        
        salary = random.choice(salaries_pool)
        exp = random.choice(experiences_pool)
        desc = random.choice(descriptions_pool)
        source = random.choice(["Indeed", "Naukri"])
        
        # Distribute posting dates over past 30 days
        post_days_ago = random.randint(0, 30)
        posted_date = (today - timedelta(days=post_days_ago)).strftime("%Y-%m-%d")
        
        job_id = f"mock_{random.randint(10000000, 99999999)}"
        
        mock_jobs.append({
            "job_id": job_id,
            "job_title": title,
            "company_name": company,
            "location": city,
            "salary": salary,
            "experience_required": exp,
            "job_description": desc,
            "skills": skills_str,
            "job_type": "Remote" if city == "Remote" else random.choice(["Full-time", "Contract", "Part-time"]),
            "posted_date": posted_date,
            "source": source,
            "scraped_at": datetime.now().isoformat()
        })
        
    return mock_jobs

def run_extraction() -> List[Dict[str, Any]]:
    """Runs extraction for all configurations, utilizing mock data if needed."""
    all_jobs = []
    
    if MOCK_DATA_FALLBACK:
        logger.info("Mock Data Fallback is enabled in config. Generating mock data directly.")
        return generate_mock_jobs(120) # Generate a robust initial batch of jobs
        
    logger.info("Starting live job extraction...")
    
    for role in JOB_ROLES:
        for city in CITIES:
            if city == "Remote":
                continue # scrape general, handle remote parsing
            
            naukri_jobs = scrape_naukri(role, city)
            indeed_jobs = scrape_indeed(role, city)
            
            all_jobs.extend(naukri_jobs)
            all_jobs.extend(indeed_jobs)
            
    # If live scraping failed to return anything (due to CAPTCHA or blocking), fallback to mock data
    if not all_jobs:
        logger.warning("Live scraping returned 0 results. Triggering mock fallback to populate system...")
        all_jobs = generate_mock_jobs(120)
        
    logger.info(f"Extraction completed. Total raw records fetched: {len(all_jobs)}")
    return all_jobs

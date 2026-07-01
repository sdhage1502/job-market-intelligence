# Job Transformation module for Automated Job Market Platform

import re
from datetime import datetime
from typing import Dict, Any, List
from scraper.utils import logger, generate_job_hash

def clean_text(text: str) -> str:
    """Removes duplicate spaces, newlines, and strips text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_city(city_str: str) -> str:
    """Standardizes city names as specified in normalizations."""
    city = clean_text(city_str).lower()
    
    if "bangalore" in city or "bengaluru" in city:
        return "bengaluru"
    elif "pune" in city:
        return "pune"
    elif "mumbai" in city or "bombay" in city:
        return "mumbai"
    elif "hyderabad" in city:
        return "hyderabad"
    elif "delhi" in city or "ncr" in city or "noida" in city or "gurgaon" in city or "gurugram" in city:
        return "delhi ncr"
    elif "chennai" in city:
        return "chennai"
    elif "remote" in city:
        return "remote"
    
    return city

def parse_experience_range(exp_str: str) -> Dict[str, Any]:
    """
    Parses experience required string into min and max integer bounds.
    Example: '3-5 years' -> {'min_exp': 3, 'max_exp': 5}
             '8+ years'  -> {'min_exp': 8, 'max_exp': 15}
    """
    exp = clean_text(exp_str).lower()
    
    # Defaults
    min_exp = None
    max_exp = None
    
    # Try parsing range e.g. "3-5"
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', exp)
    if range_match:
        min_exp = int(range_match.group(1))
        max_exp = int(range_match.group(2))
    else:
        # Try parsing single plus e.g. "8+"
        plus_match = re.search(r'(\d+)\s*\+', exp)
        if plus_match:
            min_exp = int(plus_match.group(1))
            max_exp = min_exp + 5  # Arbitrary threshold for upper bounds
        else:
            # Try parsing any single number
            single_match = re.search(r'(\d+)', exp)
            if single_match:
                min_exp = int(single_match.group(1))
                max_exp = min_exp

    return {"min_exp": min_exp, "max_exp": max_exp}

def clean_skills(skills_raw: str, description: str) -> str:
    """
    Splits skills, lowercases them, removes duplicate spaces.
    If skills_raw is empty, attempts to parse skills from job description text.
    """
    skills_list = []
    
    # Populate initial list if raw skills exist
    if skills_raw:
        # Split by comma or semicolon
        raw_list = re.split(r'[,;]+', skills_raw)
        skills_list = [clean_text(s).lower() for s in raw_list if s.strip()]
        
    # If skills are empty, look inside description for key tech words
    if not skills_list and description:
        desc_lower = description.lower()
        known_skills = [
            "sql", "python", "power bi", "tableau", "excel", "dbt", "aws", 
            "azure", "gcp", "spark", "hadoop", "scala", "java", "javascript", 
            "git", "docker", "kubernetes", "airflow", "snowflake", "postgresql"
        ]
        for skill in known_skills:
            # Word boundary check e.g. \bsql\b
            if re.search(r'\b' + re.escape(skill) + r'\b', desc_lower):
                skills_list.append(skill)
                
    # Deduplicate and sort
    skills_list = sorted(list(set(skills_list)))
    return ", ".join(skills_list)

def clean_salary_text(salary_raw: str) -> str:
    """Cleans salary formatting text."""
    val = clean_text(salary_raw)
    if not val or val.lower() in ("not disclosed", "competitive salary", "disclosed later", "null"):
        return "Not Disclosed"
    return val

def transform_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms and standardizes a single raw job card.
    Calculates the job_hash using hash(title + company + location + posted_date).
    """
    # Standardize string fields
    title = clean_text(job.get("job_title", ""))
    company = clean_text(job.get("company_name", ""))
    raw_location = clean_text(job.get("location", ""))
    location = normalize_city(raw_location)
    
    posted_date = job.get("posted_date")
    if not posted_date:
        posted_date = datetime.today().strftime("%Y-%m-%d")
        
    description = clean_text(job.get("job_description", ""))
    
    # Process skills
    skills_raw = job.get("skills", "")
    skills = clean_skills(skills_raw, description)
    
    # Process salary & experience
    salary_raw = clean_salary_text(job.get("salary", "Not Disclosed"))
    experience_raw = clean_text(job.get("experience_required", ""))
    
    # Generate unique hash
    job_hash = generate_job_hash(title, company, location, posted_date)
    
    transformed = {
        "job_id": job.get("job_id", ""),
        "job_hash": job_hash,
        "title": title,
        "company": company,
        "location": location,
        "salary_raw": salary_raw,
        "experience_raw": experience_raw,
        "skills_raw": skills,
        "description": description,
        "source": job.get("source", "Unknown"),
        "posted_date": posted_date,
        "scraped_at": job.get("scraped_at", "")
    }
    
    # Add parsed values to make loading easier/more queryable
    exp_parsed = parse_experience_range(experience_raw)
    transformed["min_experience"] = exp_parsed["min_exp"]
    transformed["max_experience"] = exp_parsed["max_exp"]
    
    return transformed

def run_transformation(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Runs transformations on all raw jobs and filters broken entries."""
    logger.info("Starting data transformations...")
    transformed_jobs = []
    
    for job in raw_jobs:
        # Rule: Remove broken entries (must have title, company, location)
        if not job.get("job_title") or not job.get("company_name") or not job.get("location"):
            logger.debug(f"Skipping broken entry: {job}")
            continue
            
        try:
            transformed = transform_job(job)
            transformed_jobs.append(transformed)
        except Exception as e:
            logger.error(f"Error transforming job: {e}")
            
    logger.info(f"Transformation completed. Total clean jobs: {len(transformed_jobs)}")
    return transformed_jobs

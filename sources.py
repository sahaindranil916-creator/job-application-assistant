import requests
import pandas as pd

def fetch_remotive(search="", limit=50):
    response = requests.get("https://remotive.com/api/remote-jobs", timeout=20)
    response.raise_for_status()
    jobs = response.json().get("jobs", [])
    needle = search.lower().strip()
    rows = []
    for job in jobs:
        text = f"{job.get('title','')} {job.get('description','')} {job.get('category','')}".lower()
        if needle and needle not in text:
            continue
        rows.append({
            "title": str(job.get("title") or ""),
            "company": str(job.get("company_name") or ""),
            "location": str(job.get("candidate_required_location") or "Remote"),
            "source": "Remotive",
            "description": str(job.get("description") or ""),
            "apply_url": str(job.get("url") or ""),
            "remote": True
        })
        if len(rows) >= limit:
            break
    return pd.DataFrame(rows)

def standardize_csv(df):
    aliases = {
        "job title": "title", "job_title": "title",
        "company name": "company", "company_name": "company",
        "job description": "description", "job_description": "description",
        "url": "apply_url", "link": "apply_url"
    }
    df = df.rename(columns={c: aliases.get(c.lower().strip(), c.lower().strip()) for c in df.columns})
    for col in ["title", "company", "location", "source", "description", "apply_url", "remote"]:
        if col not in df.columns:
            df[col] = ""
    return df[["title", "company", "location", "source", "description", "apply_url", "remote"]]

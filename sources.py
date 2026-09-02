import requests
import pandas as pd

def fetch_remotive(search="", limit=50):
    """
    Uses Remotive's public API with its documented search and limit parameters.
    If a specific query returns no results, the function falls back to a broader
    feed so the app can still suggest related roles.
    """
    base_url = "https://remotive.com/api/remote-jobs"
    limit = min(max(int(limit), 1), 100)

    params = {"limit": limit}
    if search.strip():
        params["search"] = search.strip()

    response = requests.get(
        base_url,
        params=params,
        timeout=25,
        headers={"User-Agent": "JobApplicationAssistant/1.0"}
    )
    response.raise_for_status()
    jobs = response.json().get("jobs", [])

    # Broader fallback if the exact query has no current matches.
    if not jobs and search.strip():
        response = requests.get(
            base_url,
            params={"limit": limit},
            timeout=25,
            headers={"User-Agent": "JobApplicationAssistant/1.0"}
        )
        response.raise_for_status()
        jobs = response.json().get("jobs", [])

    rows = []
    for job in jobs:
        rows.append({
            "title": str(job.get("title") or ""),
            "company": str(job.get("company_name") or ""),
            "location": str(job.get("candidate_required_location") or "Remote"),
            "source": "Remotive",
            "description": str(job.get("description") or ""),
            "apply_url": str(job.get("url") or ""),
            "remote": True
        })

    return pd.DataFrame(rows)

def standardize_csv(df):
    aliases = {
        "job title": "title", "job_title": "title",
        "company name": "company", "company_name": "company",
        "job description": "description", "job_description": "description",
        "url": "apply_url", "link": "apply_url"
    }
    df = df.rename(columns={
        c: aliases.get(c.lower().strip(), c.lower().strip())
        for c in df.columns
    })
    for col in [
        "title", "company", "location", "source",
        "description", "apply_url", "remote"
    ]:
        if col not in df.columns:
            df[col] = ""
    return df[
        ["title", "company", "location", "source",
         "description", "apply_url", "remote"]
    ]

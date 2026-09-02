import re

def clean(value):
    return re.sub(r"\s+", " ", str(value).lower()).strip()

def score_job(job, keywords):
    title = clean(job.get("title", ""))
    text = clean(f"{job.get('title','')} {job.get('description','')} {job.get('location','')}")
    matched = [clean(k) for k in keywords if clean(k) and clean(k) in text]
    coverage = len(matched) / max(len(keywords), 1)
    score = coverage * 75
    if any(x in title for x in [
        "accountant", "accounting", "finance", "rtr",
        "ledger", "reconciliation", "customer service", "support"
    ]):
        score += 15
    if len(str(job.get("description", ""))) > 150:
        score += 10
    missing = [clean(k) for k in keywords if clean(k) not in matched][:12]
    return min(100, round(score)), matched[:15], missing

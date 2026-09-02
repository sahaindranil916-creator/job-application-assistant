from config import KEYWORDS

def score_job(title, description, location=""):
    text = f"{title} {description} {location}".lower()
    matched = [k for k in KEYWORDS if k.lower() in text]
    # Keyword coverage + title relevance bonus, capped at 100
    score = min(100, len(matched) * 12)
    if any(k in title.lower() for k in ["accountant", "rtr", "ledger", "finance"]):
        score = min(100, score + 15)
    return score, matched

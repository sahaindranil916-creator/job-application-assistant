def score_job(title, description, location, keywords):
    text = f"{title} {description} {location}".lower()

    matched = [k for k in keywords if k.lower() in text]

    if keywords:
        coverage = len(matched) / len(keywords)
    else:
        coverage = 0

    score = min(100, round(coverage * 100))

    title_bonus_terms = [
        "accountant", "accounting", "rtr", "finance",
        "ledger", "reconciliation", "customer service"
    ]
    if any(term in title.lower() for term in title_bonus_terms):
        score = min(100, score + 15)

    missing = [k for k in keywords if k not in matched][:10]
    return score, matched, missing

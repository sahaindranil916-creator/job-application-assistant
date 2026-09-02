def generate_cover_letter(job, resume_text):
    title = job.get("title", "this role")
    company = job.get("company", "your organisation")
    profile = "I have professional experience and skills described accurately in my resume."
    if resume_text:
        lines = [x.strip() for x in resume_text.splitlines() if x.strip()]
        profile = " ".join(lines[:8])[:850]
    return (
        f"Dear Hiring Team,\\n\\n"
        f"I am writing to express my interest in the {title} position at {company}.\\n\\n"
        f"My application is based on my actual professional experience and the information in my resume. "
        f"I am interested in this opportunity because its requirements appear relevant to my background.\\n\\n"
        f"Relevant profile from my resume:\\n{profile}\\n\\n"
        f"I would welcome the opportunity to discuss how my skills and experience can contribute to the role. "
        f"Thank you for your time and consideration.\\n\\n"
        f"Sincerely,\\n[Your Name]"
    )

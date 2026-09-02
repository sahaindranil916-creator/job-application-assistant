import re
from pypdf import PdfReader
from config import DEFAULT_KEYWORDS, MAX_KEYWORDS

def extract_resume_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def build_keywords(resume_text):
    text = resume_text.lower()
    found = [k for k in DEFAULT_KEYWORDS if k in text]

    # Add useful multi-word terms found in the resume.
    phrases = re.findall(r"\b[A-Za-z]{3,}(?:\s+[A-Za-z]{3,}){1,2}\b", resume_text)
    for phrase in phrases:
        p = phrase.lower().strip()
        if p not in found and len(found) < MAX_KEYWORDS:
            found.append(p)

    return found[:MAX_KEYWORDS]

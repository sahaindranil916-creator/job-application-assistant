import re
from pypdf import PdfReader
from config import DEFAULT_KEYWORDS

def extract_resume_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def build_keywords(text):
    lower = text.lower()
    found = [k for k in DEFAULT_KEYWORDS if k in lower]
    words = re.findall(r"[A-Za-z][A-Za-z0-9+.#/& -]{2,50}", text)
    for word in words:
        item = " ".join(word.lower().split())
        if len(found) >= 35:
            break
        if any(token in item for token in [
            "account", "reconcil", "ledger", "finance", "audit",
            "customer", "process", "sap", "salesforce", "dynamics", "asset"
        ]) and item not in found:
            found.append(item)
    return found[:35]

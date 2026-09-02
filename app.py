import streamlit as st
import pandas as pd
from datetime import date
from resume_parser import extract_resume_text, build_keywords
from scoring import score_job
from config import DEFAULT_KEYWORDS

st.set_page_config(page_title="Job Application Assistant", layout="wide")
st.title("Job Application Assistant V3")
st.caption("Upload Resume → Match Jobs → Review → Track")

st.sidebar.header("Your Profile")
resume_file = st.sidebar.file_uploader("Upload your resume (PDF)", type=["pdf"])

if resume_file:
    try:
        resume_text = extract_resume_text(resume_file)
        keywords = build_keywords(resume_text)
        st.sidebar.success("Resume analysed successfully")
    except Exception as e:
        st.sidebar.error(f"Could not read the PDF: {e}")
        keywords = DEFAULT_KEYWORDS
else:
    keywords = DEFAULT_KEYWORDS
    st.sidebar.info("Upload your resume for personalised matching.")

st.sidebar.write(f"**Matching keywords: {len(keywords)}**")
with st.sidebar.expander("View matching profile"):
    st.write(", ".join(keywords))

st.sidebar.header("Filters")
min_score = st.sidebar.slider("Minimum match score", 0, 100, 20)
location_filter = st.sidebar.text_input("Location contains")

st.subheader("1. Import jobs")
uploaded_jobs = st.file_uploader(
    "Upload jobs as CSV",
    type=["csv"],
    help="CSV columns recommended: title, company, location, source, description, apply_url"
)

if uploaded_jobs:
    df = pd.read_csv(uploaded_jobs)
else:
    df = pd.read_csv("sample_jobs.csv")

required = ["title", "company", "location", "source", "description", "apply_url"]
for col in required:
    if col not in df.columns:
        df[col] = ""

scores, matched_list, missing_list = [], [], []
for _, row in df.iterrows():
    score, matched, missing = score_job(
        str(row["title"]),
        str(row["description"]),
        str(row["location"]),
        keywords
    )
    scores.append(score)
    matched_list.append(", ".join(matched[:12]))
    missing_list.append(", ".join(missing[:8]))

df["match_score"] = scores
df["matched_skills"] = matched_list
df["missing_profile_keywords"] = missing_list
df["status"] = df.get("status", "To Review")
df["date_found"] = df.get("date_found", str(date.today()))

filtered = df[df["match_score"] >= min_score].copy()
if location_filter:
    filtered = filtered[
        filtered["location"].astype(str).str.contains(
            location_filter, case=False, na=False
        )
    ]

filtered = filtered.sort_values("match_score", ascending=False)

st.subheader(f"2. Matching jobs ({len(filtered)})")
st.data_editor(
    filtered,
    use_container_width=True,
    hide_index=True,
    column_config={
        "apply_url": st.column_config.LinkColumn("Apply Link"),
        "match_score": st.column_config.ProgressColumn(
            "Match Score", min_value=0, max_value=100
        )
    }
)

st.download_button(
    "Download application tracker CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="job_application_tracker.csv",
    mime="text/csv"
)

st.divider()
st.subheader("3. Application review")
st.write(
    "Use the score as a starting point. Always read the full job description "
    "and verify that your resume accurately represents your experience before applying."
)

st.info(
    "Next version: connect permitted job feeds/APIs and company career pages, "
    "then automatically import new opportunities into this dashboard."
)

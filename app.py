import streamlit as st
import pandas as pd
from datetime import date
from scoring import score_job

st.set_page_config(page_title="Job Application Assistant", layout="wide")
st.title("Job Application Assistant V2")
st.caption("Find → Match → Review → Track → Sync")

uploaded = st.file_uploader("Import jobs (CSV)", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("sample_jobs.csv")

required = ["title", "company", "location", "source", "description", "apply_url"]
for col in required:
    if col not in df.columns:
        df[col] = ""

scores, matches = [], []
for _, row in df.iterrows():
    score, matched = score_job(str(row["title"]), str(row["description"]), str(row["location"]))
    scores.append(score)
    matches.append(", ".join(matched))

df["match_score"] = scores
df["matched_skills"] = matches
df["status"] = df.get("status", "To Review")
df["date_found"] = df.get("date_found", str(date.today()))

st.sidebar.header("Filters")
min_score = st.sidebar.slider("Minimum match score", 0, 100, 15)
location = st.sidebar.text_input("Location contains")

filtered = df[df["match_score"] >= min_score].copy()
if location:
    filtered = filtered[
        filtered["location"].astype(str).str.contains(location, case=False, na=False)
    ]

filtered = filtered.sort_values("match_score", ascending=False)

st.subheader(f"Matching jobs ({len(filtered)})")
st.data_editor(
    filtered,
    use_container_width=True,
    hide_index=True,
    column_config={
        "apply_url": st.column_config.LinkColumn("Apply Link"),
        "match_score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100)
    }
)

st.download_button(
    "Download application tracker CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="job_application_tracker.csv",
    mime="text/csv"
)

st.divider()
if st.button("Sync current tracker to Google Sheets"):
    try:
        from sheets_sync import sync_dataframe_to_sheet
        name = sync_dataframe_to_sheet(filtered)
        st.success(f"Synced to Google Sheet: {name}")
    except Exception as e:
        st.error(str(e))

st.info(
    "Source connectors should use official APIs, feeds, exports, or other permitted integrations. "
    "Review application information before submitting."
)

import hashlib
from datetime import date, timedelta
import pandas as pd
import streamlit as st

from config import DEFAULT_KEYWORDS, STATUS_OPTIONS
from resume_parser import extract_resume_text, build_keywords
from scoring import score_job
from sources import fetch_remotive, standardize_csv
from cover_letter import generate_cover_letter

st.set_page_config(page_title="Job Application Assistant", page_icon="🎯", layout="wide")

COLUMNS = [
    "job_id","title","company","location","source","description",
    "apply_url","remote","match_score","matched_skills",
    "missing_profile_keywords","status","date_found",
    "date_applied","follow_up_date","notes"
]

def empty_jobs():
    return pd.DataFrame(columns=COLUMNS)

def make_id(item):
    raw = (
        f"{item.get('title','')}|{item.get('company','')}|"
        f"{item.get('apply_url','')}"
    ).lower()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def enrich(df, keywords):
    if df is None or df.empty:
        return empty_jobs()

    df = standardize_csv(df).copy()
    rows = []

    for _, row in df.iterrows():
        item = row.to_dict()
        score, matched, missing = score_job(item, keywords)
        item.update({
            "job_id": make_id(item),
            "match_score": score,
            "matched_skills": ", ".join(matched),
            "missing_profile_keywords": ", ".join(missing),
            "status": "Saved",
            "date_found": str(date.today()),
            "date_applied": "",
            "follow_up_date": "",
            "notes": ""
        })
        rows.append(item)

    return pd.DataFrame(rows)[COLUMNS].drop_duplicates(
        subset=["job_id"]
    )

def merge(old, new):
    if old.empty:
        return new
    return pd.concat(
        [old, new], ignore_index=True
    ).drop_duplicates(subset=["job_id"], keep="first")

if "jobs" not in st.session_state:
    st.session_state.jobs = empty_jobs()
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "keywords" not in st.session_state:
    st.session_state.keywords = DEFAULT_KEYWORDS.copy()
if "last_search_results" not in st.session_state:
    st.session_state.last_search_results = empty_jobs()

st.title("🎯 Job Application Assistant — Final")
st.caption("Find → Match → Review → Apply → Track")

with st.sidebar:
    st.header("Your Profile")
    resume = st.file_uploader("Upload resume (PDF)", type=["pdf"])

    if resume and st.button("Analyse resume", use_container_width=True):
        try:
            st.session_state.resume_text = extract_resume_text(resume)
            st.session_state.keywords = build_keywords(
                st.session_state.resume_text
            )
            st.success("Resume analysed successfully")
        except Exception as e:
            st.error(f"Could not analyse resume: {e}")

    st.write(
        f"**Matching keywords:** {len(st.session_state.keywords)}"
    )
    with st.expander("View matching profile"):
        st.write(", ".join(st.session_state.keywords))

tabs = st.tabs([
    "🔎 Find Jobs", "📥 Import", "📊 Dashboard",
    "📝 Review", "📄 Cover Letter"
])

with tabs[0]:
    st.subheader("Find live jobs")
    st.caption(
        "Search results are displayed below immediately. "
        "The enabled connector uses a permitted public job feed."
    )

    query = st.text_input(
        "Search term",
        placeholder="accountant, finance, reconciliation"
    )
    limit = st.slider("Maximum results", 10, 100, 50, 10)

    if st.button("Search live jobs", type="primary"):
        try:
            with st.spinner("Searching live jobs..."):
                raw = fetch_remotive(query, limit)
                results = enrich(
                    raw, st.session_state.keywords
                ).sort_values("match_score", ascending=False)

            st.session_state.last_search_results = results
            before = len(st.session_state.jobs)
            st.session_state.jobs = merge(
                st.session_state.jobs, results
            )
            added = len(st.session_state.jobs) - before

            if results.empty:
                st.warning(
                    "No current jobs were returned by the source. "
                    "Try another term or import jobs using CSV."
                )
            else:
                st.success(
                    f"Found {len(results)} jobs. "
                    f"{added} new jobs were added to your tracker."
                )
        except Exception as e:
            st.error(f"Search failed: {e}")

    results = st.session_state.last_search_results

    if not results.empty:
        st.subheader("Latest search results")
        st.caption(
            f"Showing {len(results)} jobs from your latest search."
        )

        display = results[
            [
                "title", "company", "location", "source",
                "match_score", "matched_skills", "apply_url"
            ]
        ].copy()

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "apply_url": st.column_config.LinkColumn(
                    "Official application link"
                ),
                "match_score": st.column_config.ProgressColumn(
                    "Match score", min_value=0, max_value=100
                )
            }
        )
        st.info(
            "Jobs are also saved in the Dashboard for tracking."
        )

with tabs[1]:
    st.subheader("Import jobs from CSV")
    upload = st.file_uploader(
        "Upload CSV", type=["csv"], key="csv_import"
    )

    if upload is not None and st.button("Add imported jobs"):
        try:
            new = enrich(
                pd.read_csv(upload),
                st.session_state.keywords
            )
            before = len(st.session_state.jobs)
            st.session_state.jobs = merge(
                st.session_state.jobs, new
            )
            st.success(
                f"{len(st.session_state.jobs)-before} new jobs added."
            )
        except Exception as e:
            st.error(f"Could not import file: {e}")

with tabs[2]:
    jobs = st.session_state.jobs.copy()

    if jobs.empty:
        st.info("No jobs yet. Search live jobs or import a CSV.")
    else:
        a, b, c, d = st.columns(4)
        a.metric("Total", len(jobs))
        b.metric(
            "Ready",
            int((jobs.status == "Ready to Apply").sum())
        )
        c.metric(
            "Applied",
            int((jobs.status == "Applied").sum())
        )
        d.metric(
            "Interview",
            int((jobs.status == "Interview").sum())
        )

        min_score = st.slider(
            "Minimum match score", 0, 100, 0
        )
        location = st.text_input("Location contains")
        status_filter = st.multiselect(
            "Status filter", STATUS_OPTIONS
        )

        view = jobs[jobs.match_score >= min_score].copy()

        if location:
            view = view[
                view.location.astype(str).str.contains(
                    location, case=False, na=False
                )
            ]

        if status_filter:
            view = view[view.status.isin(status_filter)]

        view = view.sort_values(
            "match_score", ascending=False
        )

        edited = st.data_editor(
            view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "apply_url": st.column_config.LinkColumn(
                    "Official application link"
                ),
                "match_score": st.column_config.ProgressColumn(
                    "Match score", min_value=0, max_value=100
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status", options=STATUS_OPTIONS
                )
            },
            disabled=[
                "job_id", "title", "company", "location",
                "source", "description", "apply_url",
                "remote", "match_score", "matched_skills",
                "missing_profile_keywords", "date_found"
            ]
        )

        if st.button("Save dashboard changes"):
            for _, row in edited.iterrows():
                mask = (
                    st.session_state.jobs.job_id == row.job_id
                )
                for field in [
                    "status", "date_applied",
                    "follow_up_date", "notes"
                ]:
                    st.session_state.jobs.loc[
                        mask, field
                    ] = row[field]
            st.success("Changes saved.")

        st.download_button(
            "Download application tracker",
            st.session_state.jobs.to_csv(
                index=False
            ).encode("utf-8"),
            "job_application_tracker.csv",
            "text/csv"
        )

with tabs[3]:
    jobs = st.session_state.jobs

    if jobs.empty:
        st.info("Add jobs first.")
    else:
        options = {
            f"{r.title} — {r.company} ({r.match_score}%)": r.job_id
            for _, r in jobs.sort_values(
                "match_score", ascending=False
            ).iterrows()
        }

        label = st.selectbox("Select job", list(options))
        selected = jobs[
            jobs.job_id == options[label]
        ].iloc[0]

        st.write(f"**Location:** {selected.location}")
        st.write(f"**Source:** {selected.source}")
        st.write(f"**Match score:** {selected.match_score}%")
        st.write(
            f"**Matched skills:** "
            f"{selected.matched_skills or 'No direct keyword match'}"
        )

        if selected.apply_url:
            st.link_button(
                "Open official application page",
                selected.apply_url
            )

        st.warning(
            "Review every application for accuracy. "
            "This app does not bypass website protections "
            "or automatically submit forms."
        )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(selected.status)
        )
        follow = st.date_input(
            "Follow-up date",
            value=date.today() + timedelta(days=7)
        )
        notes = st.text_area(
            "Notes", value=str(selected.notes)
        )

        if st.button("Save application plan"):
            mask = (
                st.session_state.jobs.job_id == selected.job_id
            )
            st.session_state.jobs.loc[
                mask, "status"
            ] = status
            st.session_state.jobs.loc[
                mask, "follow_up_date"
            ] = str(follow)
            st.session_state.jobs.loc[
                mask, "notes"
            ] = notes

            if status == "Applied":
                st.session_state.jobs.loc[
                    mask, "date_applied"
                ] = str(date.today())

            st.success("Saved.")

with tabs[4]:
    if st.session_state.jobs.empty:
        st.info("Add a job first.")
    else:
        options = {
            f"{r.title} — {r.company}": r.job_id
            for _, r in st.session_state.jobs.iterrows()
        }
        label = st.selectbox(
            "Choose a job", list(options), key="cover_job"
        )
        selected = st.session_state.jobs[
            st.session_state.jobs.job_id == options[label]
        ].iloc[0]

        if st.button("Generate truthful draft"):
            letter = generate_cover_letter(
                selected, st.session_state.resume_text
            )
            st.text_area(
                "Cover-letter draft",
                letter,
                height=420
            )
            st.caption(
                "Edit the draft and remove any statement "
                "that is not fully accurate."
            )

st.divider()
st.caption(
    "Final build: designed for human-reviewed applications "
    "using permitted data sources."
)
st.subheader("Connect Gmail")

uploaded_file = st.file_uploader(
    "Upload your Google OAuth JSON file",
    type="json"
)

if uploaded_file is not None:
    st.success("JSON file uploaded successfully!")
https://indranil-job-assistant.streamlit.app/
if uploaded_file is not None:
    st.success("JSON file uploaded successfully!")

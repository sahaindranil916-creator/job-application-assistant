# Job Application Assistant V2

A local Streamlit dashboard plus optional Google Sheets sync.

## Features
- Import jobs from permitted APIs, feeds, CSV exports, or manually supplied links
- Score jobs against your profile keywords
- Review jobs before applying
- Track application status
- Export/import CSV
- Optional Google Sheets sync

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Google Sheets
1. Create a Google Cloud project and service account.
2. Enable Google Sheets API and Google Drive API.
3. Download the service-account JSON credentials.
4. Save it as `service_account.json` in this folder.
5. Share your target Google Sheet with the service-account email.
6. Set `GOOGLE_SHEET_NAME` in `.env`.

The app intentionally does not bypass CAPTCHAs, logins, or website protections.

import os

def sync_dataframe_to_sheet(df):
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not sheet_name:
        raise ValueError("GOOGLE_SHEET_NAME is not configured.")

    import gspread

    if not os.path.exists("service_account.json"):
        raise FileNotFoundError(
            "For local use, add service_account.json. "
            "For Streamlit Cloud, configure credentials using Streamlit Secrets."
        )

    gc = gspread.service_account(filename="service_account.json")
    sh = gc.open(sheet_name)

    try:
        ws = sh.worksheet("Applications")
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="Applications", rows=1000, cols=20)

    values = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
    ws.update(values, "A1")
    return sheet_name

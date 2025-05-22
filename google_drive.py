import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Set up credentials from secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

def fetch_latest_csv():
    folder_id = st.secrets["gcp_service_account"]["folder_id"]
    service = build("drive", "v3", credentials=creds)

    # Find the most recently modified CSV file
    query = f"'{folder_id}' in parents and mimeType='text/csv'"
    results = service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        pageSize=1,
        fields="files(id, name, modifiedTime)"
    ).execute()

    files = results.get("files", [])
    if not files:
        raise FileNotFoundError("No CSV files found in the folder.")

    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    df = pd.read_csv(fh)
    return df

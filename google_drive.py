import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Set up credentials using Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

def fetch_latest_csv():
    folder_id = st.secrets["gcp_service_account"]["folder_id"]

    # Build the Drive service
    service = build("drive", "v3", credentials=creds)

    # List CSV files in the folder, sorted by last modified time
    query = f"'{folder_id}' in parents and mimeType='text/csv'"
    results = service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        pageSize=1,
        fields="files(id, name, modifiedTime)"
    ).execute()

    items = results.get("files", [])
    if not items:
        raise FileNotFoundError("No CSV files found in the folder.")

    latest_file_id = items[0]["id"]
    file_name = items[0]["name"]

    # Download the file
    request = service.files().get_media(fileId=latest_file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)

    df = pd.read_csv(fh)
    return df

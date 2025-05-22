import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import csv

# Load credentials from Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive.readonly"],
)

def fetch_latest_csv():
    # Your Drive file logic here (simplified)
    drive_service = build("drive", "v3", credentials=creds)
    # Example: Fetch a specific file ID
    file_id = st.secrets["gcp_service_account"]["file_id"]
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    df = pd.read_csv(fh)
    return df

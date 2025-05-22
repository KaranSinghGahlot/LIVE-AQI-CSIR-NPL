import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import io
from googleapiclient.http import MediaIoBaseDownload

# Load credentials from Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

def fetch_latest_csv():
    file_id = st.secrets["gcp_service_account"]["file_id"]
    drive_service = build("drive", "v3", credentials=creds)
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    df = pd.read_csv(fh)
    return df

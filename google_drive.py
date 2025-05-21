import io
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "credentials.json"
ROOT_FOLDER_ID = "1adZyYVuuOWpUbSFPbDqqVrM5VN5Yo-mc"

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=creds)

def list_folders(folder_id):
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    return response.get('files', [])

def list_csvs(folder_id):
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='text/csv'",
        orderBy="modifiedTime desc",
        fields="files(id, name, modifiedTime)"
    ).execute()
    return response.get('files', [])
def fetch_latest_csv():
    folders_level_1 = list_folders(ROOT_FOLDER_ID)
    
    # ✅ DEBUG: Print level 1 folder names (e.g., '2025')
    print("Level 1 folders:", [f['name'] for f in folders_level_1])
    
    all_csvs = []

    for f1 in folders_level_1:
        folders_level_2 = list_folders(f1['id'])  # e.g., month folders: 1, 2, 3, ...
        for f2 in folders_level_2:
            csvs = list_csvs(f2['id'])  # CSVs in that month folder
            all_csvs.extend(csvs)
    
    # ✅ DEBUG: Print all CSVs found across subfolders
    print("Found CSVs:", [f['name'] for f in all_csvs])

    if not all_csvs:
        return pd.DataFrame()

    latest_file = sorted(all_csvs, key=lambda x: x['modifiedTime'], reverse=True)[0]
    file_id = latest_file['id']
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh)


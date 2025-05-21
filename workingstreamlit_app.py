import streamlit as st
import pandas as pd
from google_drive import fetch_latest_csv
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("📡 Real-Time Air Quality Dashboard")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="refresh")

# Load latest CSV from Google Drive
try:
    df = fetch_latest_csv()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if df.empty:
    st.warning("No data found.")
    st.stop()

# Display latest real-time values
st.subheader("🟢 Latest Sensor Values")
cols = st.columns(len(df.columns))
latest = df.iloc[-1]

for i, (col, val) in enumerate(latest.items()):
    val = round(val, 2) if isinstance(val, float) else val
    cols[i].metric(label=col, value=val)

# Optional: Show timestamp if present
for time_col in ['timestamp', 'time', 'datetime']:
    if time_col in df.columns:
        st.caption(f"🕒 Last Updated: {df[time_col].iloc[-1]}")
        break

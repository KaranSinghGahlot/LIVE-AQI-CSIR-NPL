import ssl
import streamlit as st
import pandas as pd
from google_drive import fetch_latest_csv
from streamlit_autorefresh import st_autorefresh

# ─── FIX FOR SSL VERSION MISMATCH ──────────────────────────────────────────────
# Some environments (corporate proxies, mismatched OpenSSL versions, etc.)
# can trigger WRONG_VERSION_NUMBER. This forces an unverified HTTPS context.
# WARNING: this skips certificate verification. Use only if you trust your endpoint.
ssl._create_default_https_context = ssl._create_unverified_context

# ─── PAGE SETUP ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="📡 Real-Time AQI Dashboard", layout="wide")

# Custom card styling
st.markdown(
    """
    <style>
      .card {
        border: 1px solid #e5e7eb;
        padding: 1.2rem;
        border-radius: 1rem;
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        text-align: center;
      }
      .label {
        font-weight: 600;
        font-size: 1.1rem;
        color: #4b5563;
      }
      .value {
        font-size: 2rem;
        font-weight: bold;
        color: #111827;
        margin-top: 0.25rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📡 Real-Time Air Quality Dashboard")

# ─── AUTO-REFRESH ─────────────────────────────────────────────────────────────
st_autorefresh(interval=60 * 1000, key="data_refresh")

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
try:
    df = fetch_latest_csv()
except ssl.SSLError as ssl_err:
    st.error(
        "SSL error when fetching data—attempting fallback (unverified HTTPS)..."
    )
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if df.empty:
    st.warning("No data found.")
    st.stop()

# ─── COLUMN DETECTION ─────────────────────────────────────────────────────────
time_col = None
for candidate in ['time','Time','timestamp','Timestamp','datetime','DateTime']:
    if candidate in df.columns:
        time_col = candidate
        break

if time_col is None:
    st.error("No valid time column found in your data.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

gas_cols = ['NOX Conc', 'NO2 Conc', 'NO Conc']
required_columns = [time_col] + gas_cols

missing = set(required_columns) - set(df.columns)
if missing:
    st.error(f"Missing columns in data: {', '.join(missing)}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# ─── EXTRACT LATEST VALUES ────────────────────────────────────────────────────
latest = df.iloc[-1]

# ─── RENDER CARDS ─────────────────────────────────────────────────────────────
st.subheader("🟢 Latest Sensor Values")
col_time, col_nox, col_no2, col_no = st.columns(4, gap="large")

with col_time:
    st.markdown(
        f"""<div class="card">
              <div class="label">Time</div>
              <div class="value">{latest[time_col]}</div>
            </div>""",
        unsafe_allow_html=True,
    )

with col_nox:
    st.markdown(
        f"""<div class="card">
              <div class="label">NOx Conc (ppb)</div>
              <div class="value">{round(latest['NOX Conc'],2)}</div>
            </div>""",
        unsafe_allow_html=True,
    )

with col_no2:
    st.markdown(
        f"""<div class="card">
              <div class="label">NO₂ Conc (ppb)</div>
              <div class="value">{round(latest['NO2 Conc'],2)}</div>
            </div>""",
        unsafe_allow_html=True,
    )

with col_no:
    st.markdown(
        f"""<div class="card">
              <div class="label">NO Conc (ppb)</div>
              <div class="value">{round(latest['NO Conc'],2)}</div>
            </div>""",
        unsafe_allow_html=True,
    )

import os
import hashlib
import hmac
import json
import secrets
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# MONEYFLOW - END-TO-END STREAMLIT DASHBOARD
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="MoneyFlow",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Paths
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "device_sessions.json"
USERS_DIR = DATA_DIR / "users"
USERS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "historical_monthly_financials.csv"

# -----------------------------
# Theme / CSS
# -----------------------------
st.markdown(
    """
    <style>
    html, body, .stApp {
        font-family: "Times New Roman", Times, serif;
    }

    /* Apply Times New Roman only to user-visible text, never Streamlit icon glyphs. */
    .stApp p, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp input, .stApp textarea,
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"],
    .stApp [data-testid="stCaptionContainer"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    /* Restore Streamlit's Material Symbols so icons render as icons, not words. */
    [data-testid="stIconMaterial"],
    span[data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", sans-serif !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }


    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(79,70,229,.10), transparent 24%),
            radial-gradient(circle at 100% 10%, rgba(14,165,164,.10), transparent 24%),
            linear-gradient(135deg, #f8faff 0%, #eef2ff 50%, #f0fdfa 100%);
        color: #172033;
    }

    [data-testid="stHeader"] {
        background: rgba(248,250,255,.88);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 55%, #064e3b 100%);
        border-right: 1px solid rgba(255,255,255,.12);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
        font-family: "Times New Roman", Times, serif !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 13px;
        padding: 9px 12px;
        margin: 4px 0;
        transition: .2s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.10);
    }

    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 12px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
        border: 1px solid #dfe5f1;
        background: rgba(255,255,255,.94);
        box-shadow: 0 10px 30px rgba(15,23,42,.065);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8faff 100%);
        border: 1px solid #dce3f0;
        border-radius: 18px;
        padding: 17px;
        box-shadow: 0 8px 24px rgba(15,23,42,.055);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 900 !important;
    }

    .moneyflow-title {
        font-size: 38px;
        font-weight: 900;
        letter-spacing: -.5px;
        color: #111827;
        margin-bottom: 4px;
    }

    .moneyflow-subtitle {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 900;
        color: #172033;
        margin: 6px 0 12px 0;
    }

    .small-muted {
        color: #64748b;
        font-size: 13px;
    }

    .hero {
        padding: 25px 28px;
        border-radius: 24px;
        background: linear-gradient(135deg, #111827 0%, #3730a3 55%, #047857 100%);
        color: white;
        box-shadow: 0 18px 40px rgba(49,46,129,.20);
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white !important;
        font-size: 38px;
        margin: 5px 0;
    }

    .hero p {
        color: #dbeafe !important;
        font-size: 16px;
        margin: 0;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,.15);
        color: white;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(255,255,255,.20);
    }

    .insight-box {
        padding: 14px 16px;
        border-radius: 15px;
        background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%);
        border: 1px solid #d9e1ff;
        margin-bottom: 10px;
        color: #25304a;
        font-size: 15px;
    }

    .ai-cfo-box {
        padding: 20px;
        border-radius: 20px;
        background: linear-gradient(135deg, #f5f3ff 0%, #eef2ff 48%, #ecfeff 100%);
        border: 1px solid #c7d2fe;
        box-shadow: 0 10px 28px rgba(79,70,229,.10);
    }

    .ai-cfo-title {
        color: #312e81;
        font-size: 25px;
        font-weight: 900;
        margin-bottom: 2px;
    }

    .ai-cfo-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .status-good {
        color: #15803d;
        font-weight: 800;
    }

    .status-warning {
        color: #b45309;
        font-weight: 800;
    }

    .status-danger {
        color: #b91c1c;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 13px !important;
        font-weight: 800 !important;
        border: 1px solid #d6deeb !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5, #0f766e) !important;
        color: white !important;
        border: none !important;
    }

    input, textarea, [data-baseweb="select"] > div {
        border-radius: 12px !important;
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 16px !important;
        line-height: 1.45 !important;
        caret-color: #4f46e5 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stMultiSelect"] label,
    [data-testid="stFileUploader"] label,
    [data-testid="stTextArea"] label {
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        overflow: hidden;
    }

    .stAlert {
        border-radius: 14px !important;
    }

    .stMarkdown, .stCaption {
        color: #1f2937;
    }



    /* ---------- PREMIUM SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 15% 4%, rgba(99,102,241,.30), transparent 28%),
            radial-gradient(circle at 85% 88%, rgba(20,184,166,.24), transparent 30%),
            linear-gradient(180deg, #0b1225 0%, #151d3b 55%, #0b302b 100%) !important;
        border-right: 1px solid rgba(255,255,255,.10) !important;
        box-shadow: 8px 0 30px rgba(15,23,42,.12);
    }

    .mf-sidebar-brand {
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 8px 8px 18px;
    }

    .mf-logo {
        width: 48px;
        height: 48px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        color: white;
        font-size: 25px;
        font-weight: 900;
        box-shadow: 0 8px 22px rgba(99,102,241,.35);
    }

    .mf-brand-name {
        color: #fff;
        font-size: 27px;
        font-weight: 900;
        line-height: 1;
    }

    .mf-brand-sub {
        color: #a5b4fc;
        font-size: 12px;
        margin-top: 5px;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,.10) !important;
        margin: 8px 0 15px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 6px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-height: 49px !important;
        box-sizing: border-box !important;
        margin: 2px 0 !important;
        padding: 0 15px !important;
        border-radius: 14px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #dbe4ff !important;
        cursor: pointer !important;
        transition: all .18s ease !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.09) !important;
        border-color: rgba(255,255,255,.10) !important;
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(99,102,241,.35), rgba(20,184,166,.18)) !important;
        border-color: rgba(129,140,248,.35) !important;
        box-shadow: inset 3px 0 0 #818cf8, 0 8px 22px rgba(2,6,23,.15) !important;
        color: #fff !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child,
    [data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
        display: none !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: inherit !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }

    [data-testid="stSidebar"] .stButton {
        margin-top: 18px !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 46px !important;
        border-radius: 13px !important;
        background: rgba(255,255,255,.08) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,.16) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(248,113,113,.18) !important;
        border-color: rgba(248,113,113,.38) !important;
    }

    [data-testid="stSidebar"] .stButton > button p {
        color: #fff !important;
        font-weight: 800 !important;
    }

    .mf-sidebar-user {
        padding: 13px 14px;
        margin-top: 14px;
        border-radius: 14px;
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.10);
        color: #cbd5e1;
        font-size: 12px;
    }

    .mf-sidebar-user strong {
        color: #fff;
        font-size: 13px;
    }

    /* ---------- PREMIUM DATA CARD ---------- */
    .data-hero {
        padding: 20px 22px;
        border-radius: 18px;
        background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%);
        border: 1px solid #c7d2fe;
        margin-bottom: 15px;
    }

    .data-hero-title {
        font-size: 25px;
        font-weight: 900;
        color: #172554;
    }

    .data-hero-sub {
        margin-top: 5px;
        color: #64748b;
        font-size: 14px;
    }

    .data-status {
        display: inline-flex;
        margin-top: 12px;
        padding: 7px 11px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-weight: 800;
        font-size: 12px;
    }

    .data-source-card {
        padding: 15px 17px;
        border-radius: 15px;
        background: #fff;
        border: 1px solid #dbe3ef;
        box-shadow: 0 7px 22px rgba(15,23,42,.045);
        margin-bottom: 14px;
    }

    .data-source-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .5px;
    }

    .data-source-value {
        color: #1e293b;
        font-size: 14px;
        font-weight: 700;
        margin-top: 7px;
        overflow-wrap: anywhere;
    }

    .settings-stat {
        padding: 15px;
        border-radius: 15px;
        background: linear-gradient(145deg,#fff,#f8fafc);
        border: 1px solid #dbe3ef;
    }

    .settings-stat-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 800;
    }

    .settings-stat-value {
        color: #172033;
        font-size: 23px;
        font-weight: 900;
        margin-top: 3px;
    }

    /* ---------- Sidebar visibility ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10182d 0%, #172554 58%, #12372f 100%) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        padding: 10px 12px !important;
        min-height: 44px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.10) !important;
        border-color: rgba(255,255,255,.12) !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: rgba(255,255,255,.16) !important;
        border-color: rgba(255,255,255,.20) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #ffffff !important;
        font-weight: 900 !important;
        min-height: 44px !important;
    }

    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span:not([data-testid="stIconMaterial"]) {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #dbeafe !important;
        opacity: 1 !important;
    }

    /* ---------- Clean widget text ---------- */
    .stButton > button {
        min-height: 44px !important;
        overflow: hidden !important;
    }

    .stButton > button p {
        margin: 0 !important;
        white-space: normal !important;
        line-height: 1.2 !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        min-width: 120px !important;
        padding: 8px 14px !important;
    }

    [data-testid="stFileUploaderDropzone"] button p {
        white-space: nowrap !important;
    }

    /* Password visibility icon / eye must remain visible. */
    [data-testid="stTextInput"] button,
    [data-testid="stTextInput"] button span,
    [data-testid="stTextInput"] button [data-testid="stIconMaterial"] {
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Make expander label readable and prevent icon text collision. */
    [data-testid="stExpander"] summary {
        min-height: 46px !important;
        align-items: center !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] summary p {
        margin: 0 !important;
        font-weight: 800 !important;
    }

    @media (max-width: 768px) {
        .moneyflow-title { font-size: 29px; }
        .hero h1 { font-size: 29px; }
        .hero { padding: 20px; }
        [data-testid="stMetricValue"] { font-size: 24px !important; }
        [data-testid="stSidebar"] { min-width: 250px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Session state
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "selected_transaction" not in st.session_state:
    st.session_state.selected_transaction = None

if "settings" not in st.session_state:
    st.session_state.settings = {"theme":"Light","currency":"INR (₹)","date_format":"DD-MM-YYYY","financial_alerts":True,"risk_alerts":True,"forecast_alerts":True,"ai_alerts":True,"biometric":False,"remember_device":True,"ai_suggestions":True,"automatic_explanations":True,"forecast_insights":True}


def _read_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    temp.replace(path)


def _load_users():
    return _read_json(USERS_FILE, {})


def _save_users(users):
    _write_json(USERS_FILE, users)


def _device_key():
    # Streamlit does not expose a writable browser cookie API here.
    # Use the browser/device user-agent as a lightweight local prototype key.
    try:
        headers = dict(st.context.headers)
        user_agent = headers.get("User-Agent", "unknown-device")
    except Exception:
        user_agent = "unknown-device"
    return hashlib.sha256(user_agent.encode("utf-8")).hexdigest()[:24]


def _user_key(identifier):
    return hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()[:24]


def _user_dir(identifier=None):
    identifier = identifier or st.session_state.user_email
    folder = USERS_DIR / _user_key(identifier)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _user_transactions_file(identifier=None):
    return _user_dir(identifier) / "transactions.csv"


def _start_login(identifier, user):
    identifier = identifier.strip().lower()
    st.session_state.logged_in = True
    st.session_state.user_email = identifier
    st.session_state.user_name = user.get("name", "MoneyFlow User")
    st.session_state.auth_mode = "login"

    sessions = _read_json(SESSIONS_FILE, {})
    device = _device_key()
    token = secrets.token_urlsafe(32)
    sessions[device] = {"token": token, "user": identifier}
    _write_json(SESSIONS_FILE, sessions)


def _restore_login():
    if st.session_state.logged_in:
        return
    sessions = _read_json(SESSIONS_FILE, {})
    saved = sessions.get(_device_key())
    if not saved:
        return
    identifier = saved.get("user", "")
    users = _load_users()
    user = users.get(identifier)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_email = identifier
        st.session_state.user_name = user.get("name", "MoneyFlow User")


def _clear_login():
    device = _device_key()
    sessions = _read_json(SESSIONS_FILE, {})
    sessions.pop(device, None)
    _write_json(SESSIONS_FILE, sessions)
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = "User"
    st.session_state.auth_mode = "login"

# Do not auto-restore a previous account. Each new app session starts at login.
# Apply the selected theme to the actual Streamlit interface.
_current_theme = st.session_state.settings.get("theme", "Light")
if _current_theme == "Dark":
    st.markdown("""
    <style>
    .stApp { background: #0b1120 !important; color: #e5e7eb !important; }
    [data-testid="stHeader"] { background: rgba(11,17,32,.92) !important; }
    [data-testid="stMain"] { background: #0b1120 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { background: #111827 !important; border-color: #263244 !important; box-shadow: none !important; }
    div[data-testid="stMetric"] { background: #111827 !important; border-color: #263244 !important; box-shadow: none !important; }
    div[data-testid="stMetricLabel"], [data-testid="stMetricValue"], .moneyflow-title, .section-title { color: #f8fafc !important; }
    .moneyflow-subtitle, .small-muted, .stCaption, [data-testid="stCaptionContainer"] { color: #94a3b8 !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown li, label { color: #e5e7eb !important; }
    input, textarea, [data-baseweb="select"] > div { background: #0f172a !important; color: #f8fafc !important; border-color: #334155 !important; }
    [data-baseweb="popover"], [role="listbox"] { background: #111827 !important; color: #f8fafc !important; }
    [role="option"] { color: #f8fafc !important; }
    .insight-box, .data-source-card { background: #172033 !important; border-color: #334155 !important; color: #e5e7eb !important; }
    .ai-cfo-box { background: linear-gradient(135deg,#172033,#1e1b4b,#12372f) !important; border-color: #3730a3 !important; }
    .ai-cfo-title { color: #c7d2fe !important; }
    [data-testid="stDataFrame"] { border-color: #334155 !important; }
    </style>
    """, unsafe_allow_html=True)
elif _current_theme == "System default":
    st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        .stApp { background: #0b1120 !important; color: #e5e7eb !important; }
        [data-testid="stMain"] { background: #0b1120 !important; }
        [data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stMetric"] { background: #111827 !important; border-color: #263244 !important; box-shadow: none !important; }
        .moneyflow-title, .section-title, div[data-testid="stMetricValue"] { color: #f8fafc !important; }
        .moneyflow-subtitle, [data-testid="stCaptionContainer"] { color: #94a3b8 !important; }
        input, textarea, [data-baseweb="select"] > div { background: #0f172a !important; color: #f8fafc !important; border-color: #334155 !important; }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# DATA FUNCTIONS
# ============================================================

def _datasets_file(identifier=None):
    return _user_dir(identifier) / "datasets.json"


def _dataset_folder(identifier=None):
    folder = _user_dir(identifier) / "datasets"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _read_datasets(identifier=None):
    path = _datasets_file(identifier)
    data = _read_json(path, [])
    if not isinstance(data, list):
        data = []
    return data


def _write_datasets(data, identifier=None):
    _write_json(_datasets_file(identifier), data)


def _dataset_categories(df):
    if df is None or df.empty or "category" not in df.columns:
        return []
    return sorted({str(x).strip().casefold() for x in df["category"].dropna() if str(x).strip()})


def _dataset_file(dataset_id, identifier=None):
    return _dataset_folder(identifier) / f"dataset_{dataset_id}.csv"


def _ensure_dataset_registry(identifier=None):
    """Create/migrate the per-user dataset registry without deleting existing data."""
    identifier = identifier or st.session_state.get("user_email", "")
    if not identifier:
        return []

    datasets = _read_datasets(identifier)
    if datasets:
        return datasets

    legacy = _user_transactions_file(identifier)
    if legacy.exists():
        try:
            old = pd.read_csv(legacy)
        except Exception:
            old = pd.DataFrame()
        if not old.empty:
            dataset_id = "dataset_1"
            target = _dataset_file(dataset_id, identifier)
            old.to_csv(target, index=False)
            meta = [{
                "id": dataset_id,
                "name": "Dataset 1",
                "categories": _dataset_categories(old),
                "rows": int(len(old)),
            }]
            _write_datasets(meta, identifier)
            return meta

    return []


def _active_dataset_id(identifier=None):
    identifier = identifier or st.session_state.get("user_email", "")
    datasets = _ensure_dataset_registry(identifier)
    if not datasets:
        return None
    current = st.session_state.get("active_dataset_id")
    ids = [d.get("id") for d in datasets]
    if current not in ids:
        current = ids[0]
        st.session_state.active_dataset_id = current
    return current


def _set_active_dataset(dataset_id):
    st.session_state.active_dataset_id = dataset_id


def _load_dataset_by_id(dataset_id, identifier=None):
    empty = pd.DataFrame(columns=["id", "date", "description", "category", "type", "amount"])
    if not dataset_id:
        return empty
    path = _dataset_file(dataset_id, identifier)
    if not path.exists():
        return empty
    try:
        df = pd.read_csv(path)
    except Exception:
        return empty
    required = ["id", "date", "description", "category", "type", "amount"]
    for col in required:
        if col not in df.columns:
            df[col] = range(1, len(df) + 1) if col == "id" else ""
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["type"] = df["type"].astype(str).str.strip().str.title()
    df["category"] = df["category"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()
    df = df.dropna(subset=["date", "amount"])
    df = df[df["amount"] > 0]
    df = df[df["type"].isin(["Income", "Expense"])]
    df = df.drop_duplicates()
    return df.sort_values("date").reset_index(drop=True)


def load_transactions():
    identifier = st.session_state.get("user_email", "")
    if not identifier:
        return pd.DataFrame(columns=["id", "date", "description", "category", "type", "amount"])
    dataset_id = _active_dataset_id(identifier)
    return _load_dataset_by_id(dataset_id, identifier)


@st.cache_data
def load_history():
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=["month", "income", "expenses"])
    df = pd.read_csv(HISTORY_FILE)
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df["income"] = pd.to_numeric(df["income"], errors="coerce")
    df["expenses"] = pd.to_numeric(df["expenses"], errors="coerce")
    df = df.dropna(subset=["month", "income", "expenses"])
    df["profit"] = df["income"] - df["expenses"]
    return df.sort_values("month").reset_index(drop=True)


def save_transactions(df):
    identifier = st.session_state.get("user_email", "")
    if not identifier:
        return
    dataset_id = _active_dataset_id(identifier)
    if not dataset_id:
        datasets = _read_datasets(identifier)
        dataset_id = "dataset_1"
        datasets.append({"id": dataset_id, "name": "Dataset 1", "categories": _dataset_categories(df), "rows": 0})
        _write_datasets(datasets, identifier)
        st.session_state.active_dataset_id = dataset_id
    output = df.copy()
    output["date"] = pd.to_datetime(output["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    output.to_csv(_dataset_file(dataset_id, identifier), index=False)
    datasets = _read_datasets(identifier)
    for item in datasets:
        if item.get("id") == dataset_id:
            item["categories"] = _dataset_categories(output)
            item["rows"] = int(len(output))
    _write_datasets(datasets, identifier)


def _merge_into_dataset(dataset_id, clean, identifier=None):
    existing = _load_dataset_by_id(dataset_id, identifier)
    combined = pd.concat([existing, clean], ignore_index=True)
    combined = combined.drop_duplicates(subset=["date", "description", "category", "type", "amount"]).copy()
    combined["id"] = range(1, len(combined) + 1)
    combined = combined[["id", "date", "description", "category", "type", "amount"]]
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined.to_csv(_dataset_file(dataset_id, identifier), index=False)
    return combined


def _create_dataset(clean, name, identifier=None):
    datasets = _read_datasets(identifier)
    numbers = []
    for item in datasets:
        try:
            numbers.append(int(str(item.get("name", "")).split()[-1]))
        except Exception:
            pass
    number = max(numbers, default=0) + 1
    dataset_id = f"dataset_{secrets.token_hex(6)}"
    clean = clean.copy()
    clean["id"] = range(1, len(clean) + 1)
    clean = clean[["id", "date", "description", "category", "type", "amount"]]
    clean.to_csv(_dataset_file(dataset_id, identifier), index=False)
    datasets.append({
        "id": dataset_id,
        "name": f"Dataset {number}",
        "categories": _dataset_categories(clean),
        "rows": int(len(clean)),
    })
    _write_datasets(datasets, identifier)
    return dataset_id


def money(value):
    return f"₹{value:,.0f}"


def percentage(value):
    return f"{value:.1f}%"


def financial_summary(df):
    income = df.loc[df["type"] == "Income", "amount"].sum()
    expenses = df.loc[df["type"] == "Expense", "amount"].sum()
    profit = income - expenses
    margin = (profit / income * 100) if income else 0
    expense_ratio = (expenses / income * 100) if income else 0
    return income, expenses, profit, margin, expense_ratio


def monthly_data(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "Income", "Expense", "Profit"])

    x = df.copy()
    x["month"] = x["date"].dt.to_period("M").astype(str)

    result = (
        x.groupby(["month", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    if "Income" not in result:
        result["Income"] = 0
    if "Expense" not in result:
        result["Expense"] = 0

    result["Profit"] = result["Income"] - result["Expense"]
    return result.sort_values("month")


def risk_analysis(df):
    expenses = df[df["type"] == "Expense"].copy()

    if expenses.empty:
        return expenses, {"High": 0, "Medium": 0, "Low": 0}, "Low"

    mean = expenses["amount"].mean()
    std = expenses["amount"].std()

    if pd.isna(std):
        std = 0

    medium_threshold = mean + std
    high_threshold = mean + 2 * std

    def level(amount):
        if amount > high_threshold:
            return "High"
        if amount > medium_threshold:
            return "Medium"
        return "Low"

    expenses["risk_level"] = expenses["amount"].apply(level)

    counts = expenses["risk_level"].value_counts().to_dict()
    counts = {
        "High": counts.get("High", 0),
        "Medium": counts.get("Medium", 0),
        "Low": counts.get("Low", 0),
    }

    if counts["High"] >= 2:
        overall = "High"
    elif counts["High"] == 1 or counts["Medium"] >= 2:
        overall = "Medium"
    else:
        overall = "Low"

    return expenses, counts, overall


def build_insights(df):
    income, expenses, profit, margin, ratio = financial_summary(df)
    insights = []

    if income > 0:
        insights.append(
            f"Your current profit is {money(profit)}, giving you a profit margin of {margin:.1f}%."
        )

    if ratio > 50:
        insights.append(
            f"Expenses are {ratio:.1f}% of income. Review recurring costs and large expense categories."
        )
    else:
        insights.append(
            f"Expenses are {ratio:.1f}% of income, leaving {100-ratio:.1f}% of income after expenses."
        )

    category = (
        df[df["type"] == "Expense"]
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if not category.empty:
        top_category = category.index[0]
        top_amount = category.iloc[0]
        insights.append(
            f"{top_category} is currently your largest expense category at {money(top_amount)}."
        )

    _, _, overall = risk_analysis(df)
    insights.append(f"Current transaction risk level is {overall}.")

    return insights


# ============================================================
# AUTHENTICATION
# ============================================================


def _send_password_reset_code(email_address, code):
    """Send a real password-reset code through configured SMTP email."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()

    if not smtp_user or not smtp_password:
        raise RuntimeError(
            "Password-reset email is not configured. Add SMTP_USER and SMTP_PASSWORD to the .env file."
        )

    message = EmailMessage()
    message["Subject"] = "MoneyFlow Password Reset Code"
    message["From"] = smtp_user
    message["To"] = email_address
    message.set_content(
        f"""Hello,\n\n"
        f"Your MoneyFlow password reset code is: {code}\n\n"
        "This code expires in 10 minutes. If you did not request a password reset, ignore this email.\n\n"
        "MoneyFlow\nAI Financial Command Center"""
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)


def _create_reset_code(email_address):
    code = f"{secrets.randbelow(1000000):06d}"
    reset_store = DATA_DIR / "password_resets.json"
    resets = _read_json(reset_store, {})
    resets[email_address] = {
        "code": code,
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
    }
    _write_json(reset_store, resets)
    return code


def _verify_reset_code(email_address, code):
    reset_store = DATA_DIR / "password_resets.json"
    resets = _read_json(reset_store, {})
    record = resets.get(email_address)
    if not record:
        return False
    try:
        expires = datetime.fromisoformat(record["expires_at"])
    except (KeyError, ValueError, TypeError):
        return False
    if datetime.utcnow() > expires:
        resets.pop(email_address, None)
        _write_json(reset_store, resets)
        return False
    return hmac.compare_digest(str(record.get("code", "")), str(code).strip())


def _consume_reset_code(email_address):
    reset_store = DATA_DIR / "password_resets.json"
    resets = _read_json(reset_store, {})
    resets.pop(email_address, None)
    _write_json(reset_store, resets)


def login_page():
    left, center, right = st.columns([1, 1.35, 1])

    with center:
        st.markdown("""<div class="hero"><span class="hero-badge">SMART FINANCE • MONEYFLOW</span><h1>💼 MoneyFlow</h1><p>Your personal financial command center.</p></div>""", unsafe_allow_html=True)

        with st.container(border=True):
            mode = st.session_state.auth_mode

            if mode == "create":
                st.subheader("Create your MoneyFlow account")
                name = st.text_input("Full name", placeholder="Your name", key="create_name")
                identifier = st.text_input("Email or phone", placeholder="you@example.com or +91 XXXXX XXXXX", key="create_identifier")
                password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="create_password")
                confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter your password", key="create_confirm")

                if st.button("Create account", use_container_width=True, type="primary", key="create_account_submit"):
                    identifier_clean = identifier.strip().lower() if identifier else ""
                    users = _load_users()
                    if not name.strip() or not identifier_clean or not password:
                        st.error("Please fill in all fields.")
                    elif len(password) < 6:
                        st.error("Password must contain at least 6 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif identifier_clean in users:
                        st.error("An account already exists with these details. Please sign in.")
                    else:
                        users[identifier_clean] = {
                            "name": name.strip(),
                            "password_hash": hashlib.sha256(password.encode("utf-8")).hexdigest(),
                        }
                        _save_users(users)
                        _user_transactions_file(identifier_clean)
                        st.session_state.auth_mode = "login"
                        st.success("Account created successfully. Please sign in.")
                        st.rerun()

                if st.button("← Back to Sign in", use_container_width=True, key="back_to_login"):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            elif mode == "forgot":
                st.subheader("Forgot your password?")
                st.caption("Enter the email address used for your MoneyFlow account. We will send a 6-digit reset code.")
                reset_email = st.text_input("Email address", placeholder="you@example.com", key="reset_email")

                if st.button("Send reset code", use_container_width=True, type="primary", key="send_reset_code"):
                    email_clean = reset_email.strip().lower() if reset_email else ""
                    users = _load_users()
                    user = users.get(email_clean)

                    if "@" not in email_clean:
                        st.error("Password reset by email requires an email account.")
                    elif user is None:
                        st.error("No MoneyFlow account was found for this email.")
                    else:
                        try:
                            code = _create_reset_code(email_clean)
                            _send_password_reset_code(email_clean, code)
                            st.session_state.reset_email = email_clean
                            st.session_state.auth_mode = "reset"
                            st.success("Reset code sent to your email.")
                            st.rerun()
                        except Exception as error:
                            st.error(f"Could not send the reset email: {error}")

                if st.button("← Back to Sign in", use_container_width=True, key="forgot_back"):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            elif mode == "reset":
                st.subheader("Reset your password")
                reset_email = st.session_state.get("reset_email", "")
                st.caption(f"Reset code sent to {reset_email}")
                code = st.text_input("6-digit reset code", max_chars=6, key="reset_code")
                new_password = st.text_input("New password", type="password", placeholder="At least 6 characters", key="reset_new_password")
                confirm_password = st.text_input("Confirm new password", type="password", key="reset_confirm_password")

                if st.button("Reset password", use_container_width=True, type="primary", key="reset_password_submit"):
                    if not _verify_reset_code(reset_email, code):
                        st.error("Invalid or expired reset code.")
                    elif len(new_password) < 6:
                        st.error("Password must contain at least 6 characters.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        users = _load_users()
                        users[reset_email]["password_hash"] = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
                        _save_users(users)
                        _consume_reset_code(reset_email)
                        st.session_state.auth_mode = "login"
                        st.session_state.reset_email = ""
                        st.success("Password reset successfully. Please sign in with your new password.")
                        st.rerun()

                if st.button("← Back to Sign in", use_container_width=True, key="reset_back"):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            else:
                st.subheader("Welcome back")
                identifier = st.text_input("Email or phone", placeholder="you@example.com or +91 XXXXX XXXXX", key="login_identifier")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

                if st.button("Sign in to MoneyFlow", use_container_width=True, type="primary", key="sign_in"):
                    identifier_clean = identifier.strip().lower() if identifier else ""
                    users = _load_users()
                    user = users.get(identifier_clean)
                    password_hash = hashlib.sha256((password or "").encode("utf-8")).hexdigest()

                    if not identifier_clean or not password:
                        st.error("Please enter your login details.")
                    elif user is None:
                        st.error("No account found. Please create an account first.")
                    elif not hmac.compare_digest(user.get("password_hash", ""), password_hash):
                        st.error("Incorrect password. Please try again.")
                    else:
                        _start_login(identifier_clean, user)
                        st.rerun()

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Create account", use_container_width=True, key="go_create"):
                        st.session_state.auth_mode = "create"
                        st.rerun()
                with c2:
                    if st.button("Forgot password?", use_container_width=True, key="forgot_password"):
                        st.session_state.auth_mode = "forgot"
                        st.rerun()

        st.caption("Create an account first. New accounts start with an empty financial workspace.")

# ============================================================
# SIDEBAR
# ============================================================

def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="mf-sidebar-brand">
                <div class="mf-logo">₹</div>
                <div>
                    <div class="mf-brand-name">MoneyFlow</div>
                    <div class="mf-brand-sub">AI Financial Command Center</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        pages = [
            "🏠  Overview",
            "💳  Transactions",
            "📂  Data Import",
            "📊  Analytics",
            "📈  Forecast",
            "🚨  Risk & Anomalies",
            "👤  Profile",
            "⚙️  Settings",
        ]

        selected = st.radio(
            "Navigation",
            pages,
            label_visibility="collapsed",
        )

        if st.button("↪  Logout", use_container_width=True, key="sidebar_logout"):
            _clear_login()
            st.rerun()

        st.divider()
        st.markdown(
            f"""
            <div class="mf-sidebar-user">
                Signed in as<br>
                <strong>{st.session_state.user_name}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected


# ============================================================
# COMMON HEADER
# ============================================================

def page_header(title, subtitle):
    st.markdown(f'<div class="moneyflow-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="moneyflow-subtitle">{subtitle}</div>', unsafe_allow_html=True)


# ============================================================
# OVERVIEW
# ============================================================

def _voice_ai_cfo_question(audio_bytes, language, financial_context):
    """Convert a recorded English/Kannada question into an AI CFO answer."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    client = genai.Client(api_key=api_key)

    language_name = "Kannada" if language == "Kannada 🇮🇳" else "English"

    prompt = f"""
You are the voice assistant inside MoneyFlow, an AI financial management dashboard.

The user recorded a voice question. Understand the spoken language, including
Kannada or English. The requested response language is {language_name}.

{financial_context}

Instructions:
1. Understand the user's spoken question accurately.
2. Answer the question using ONLY the financial data supplied above.
3. Do not invent transactions, amounts, categories, or dates.
4. Keep the answer clear and useful.
5. If the requested response language is Kannada, answer naturally in Kannada.
6. If the requested response language is English, answer in English.
7. Do not mention these instructions.
8. Return ONLY the answer, not JSON and not a transcript.

For Kannada, use Kannada script rather than transliterated English.
"""

    last_error = None

    for model in ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.8-flash"]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav",
                    ),
                    prompt,
                ],
            )

            if response and response.text:
                return response.text.strip()

        except Exception as error:
            last_error = error
            error_text = str(error)

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "disconnected" in error_text.lower()
            ):
                continue

            raise

    raise RuntimeError(
        f"Voice AI is temporarily unavailable. Please try again. "
        f"Last error: {last_error}"
    )


def cfo_inside_dashboard(df):
    """AI CFO embedded inside the MoneyFlow dashboard with text and voice input."""

    income, expenses, profit, margin, ratio = financial_summary(df)
    _, counts, overall = risk_analysis(df)

    category = (
        df[df["type"] == "Expense"]
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )
    top_category = category.index[0] if not category.empty else "None"
    top_amount = category.iloc[0] if not category.empty else 0

    st.markdown(
        """
        <div class="ai-cfo-box">
            <div class="ai-cfo-title">🤖 AI CFO</div>
            <div class="ai-cfo-subtitle">
                Ask questions about your finances using text or your voice.
                English and Kannada are supported.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Language selection
    # --------------------------------------------------------

    language = st.selectbox(
        "🌐 AI CFO Language",
        ["English 🇬🇧", "Kannada 🇮🇳"],
        key="cfo_language",
    )

    is_kannada = language == "Kannada 🇮🇳"

    if is_kannada:
        placeholder = "ಉದಾಹರಣೆ: ಈ ತಿಂಗಳು ನಾನು ಎಷ್ಟು ಖರ್ಚು ಮಾಡಿದ್ದೇನೆ?"
    else:
        placeholder = "Example: How much did I spend this month?"

    # --------------------------------------------------------
    # Financial context shared by text and voice AI
    # --------------------------------------------------------

    financial_context = f"""
You are the AI CFO inside MoneyFlow.

Use ONLY this financial data:

Total income: ₹{income:,.2f}
Total expenses: ₹{expenses:,.2f}
Net profit: ₹{profit:,.2f}
Profit margin: {margin:.2f}%
Expense ratio: {ratio:.2f}%
Overall risk: {overall}
High-risk transactions: {counts["High"]}
Medium-risk transactions: {counts["Medium"]}
Low-risk transactions: {counts["Low"]}
Largest expense category: {top_category}
Largest expense amount: ₹{top_amount:,.2f}
"""

    # --------------------------------------------------------
    # Text question
    # --------------------------------------------------------

    question = st.text_input(
        "⌨️ Ask your AI CFO",
        placeholder=placeholder,
        key="dashboard_cfo_question",
    )

    # --------------------------------------------------------
    # Voice recording
    # --------------------------------------------------------

    st.markdown("### 🎙️ Voice AI CFO")

    if is_kannada:
        st.caption("Kannada voice: ಕೆಳಗಿನ ಮೈಕ್ರೊಫೋನ್ ಬಳಸಿ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಮಾತನಾಡಿ.")
    else:
        st.caption("English voice: Click the microphone and ask your financial question.")

    audio_value = None

    try:
        audio_value = st.audio_input(
            "🎙️ Record your question",
            key="cfo_voice_input",
        )
    except AttributeError:
        st.warning(
            "Voice recording needs a newer Streamlit version. "
            "Text AI CFO is still available."
        )

    # --------------------------------------------------------
    # Quick questions
    # --------------------------------------------------------

    if is_kannada:
        quick1_text = "💸 ಖರ್ಚುಗಳು ಏಕೆ ಹೆಚ್ಚಾಗಿವೆ?"
        quick2_text = "📌 ಅತಿ ದೊಡ್ಡ ಖರ್ಚು ಯಾವುದು?"
        quick3_text = "🛡️ ನನ್ನ ಅಪಾಯವನ್ನು ವಿವರಿಸಿ"

        quick1_question = "ನನ್ನ ಖರ್ಚುಗಳು ಏಕೆ ಹೆಚ್ಚಾಗಿವೆ ಮತ್ತು ನಾನು ಯಾವುದನ್ನು ಪರಿಶೀಲಿಸಬೇಕು?"
        quick2_question = "ನನ್ನ ಅತಿ ದೊಡ್ಡ ಖರ್ಚು ಯಾವುದು ಮತ್ತು ಅದು ಏಕೆ ಮುಖ್ಯ?"
        quick3_question = "ನನ್ನ ಪ್ರಸ್ತುತ ಹಣಕಾಸಿನ ಅಪಾಯವನ್ನು ಸರಳವಾಗಿ ವಿವರಿಸಿ."
    else:
        quick1_text = "💸 Why are expenses high?"
        quick2_text = "📌 Biggest expense?"
        quick3_text = "🛡️ Explain my risk"

        quick1_question = "Why are my expenses high and what should I review?"
        quick2_question = "What is my biggest expense and why does it matter?"
        quick3_question = "Explain my current financial risk in simple language."

    quick1, quick2, quick3 = st.columns(3)

    quick_question = None

    if quick1.button(
        quick1_text,
        use_container_width=True,
        key="cfo_q1",
    ):
        quick_question = quick1_question

    if quick2.button(
        quick2_text,
        use_container_width=True,
        key="cfo_q2",
    ):
        quick_question = quick2_question

    if quick3.button(
        quick3_text,
        use_container_width=True,
        key="cfo_q3",
    ):
        quick_question = quick3_question

    # --------------------------------------------------------
    # Ask text AI CFO
    # --------------------------------------------------------

    ask_clicked = st.button(
        "✨ Ask AI CFO",
        type="primary",
        use_container_width=True,
        key="ask_cfo_button",
    )

    # --------------------------------------------------------
    # Voice AI CFO
    # --------------------------------------------------------

    voice_clicked = st.button(
        "🎙️ Ask using Voice",
        use_container_width=True,
        key="ask_cfo_voice_button",
    )

    # --------------------------------------------------------
    # Process voice question
    # --------------------------------------------------------

    if voice_clicked:

        if audio_value is None:
            st.warning(
                "Please record a voice question first."
                if not is_kannada
                else "ಮೊದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ."
            )

        else:
            try:
                audio_bytes = audio_value.getvalue()

                if not audio_bytes:
                    raise ValueError("The voice recording is empty.")

                with st.spinner(
                    "AI CFO is listening and preparing your answer..."
                    if not is_kannada
                    else "AI CFO ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳುತ್ತಿದೆ..."
                ):
                    response = _voice_ai_cfo_question(
                        audio_bytes,
                        language,
                        financial_context,
                    )

                st.markdown(
                    f'<div class="insight-box">🧠 <b>'
                    f'{"CFO ಉತ್ತರ" if is_kannada else "CFO Analysis"}'
                    f'</b><br><br>{response}</div>',
                    unsafe_allow_html=True,
                )

            except Exception as error:
                st.error(
                    f"Voice AI could not process the recording: {error}"
                )

    # --------------------------------------------------------
    # Process typed / quick question
    # --------------------------------------------------------

    final_question = quick_question or question

    if quick_question or ask_clicked:

        if not final_question or not final_question.strip():

            st.warning(
                "Enter a question first."
                if not is_kannada
                else "ಮೊದಲು ಒಂದು ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ."
            )

        else:

            response_language = (
                "Kannada" if is_kannada else "English"
            )

            context = f"""
{financial_context}

The user wants the answer in {response_language}.

Answer the user's question in simple language.
Explain the reasoning using the numbers.
Give practical financial guidance.
Do not invent transactions.

User question:
{final_question}
"""

            try:

                from src.ai_engine import ask_gemini

                with st.spinner(
                    "AI CFO is analysing your financial data..."
                    if not is_kannada
                    else "AI CFO ನಿಮ್ಮ ಹಣಕಾಸಿನ ಮಾಹಿತಿಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ..."
                ):
                    response = ask_gemini(context)

                st.markdown(
                    f'<div class="insight-box">🧠 <b>'
                    f'{"CFO ಉತ್ತರ" if is_kannada else "CFO Analysis"}'
                    f'</b><br><br>{response}</div>',
                    unsafe_allow_html=True,
                )

            except Exception:

                # Local fallback so the dashboard remains useful
                q = final_question.lower()

                if (
                    "biggest" in q
                    or "largest" in q
                    or "ಅತಿ ದೊಡ್ಡ" in q
                ):
                    if is_kannada:
                        fallback = (
                            f"ನಿಮ್ಮ ಅತಿ ದೊಡ್ಡ ಖರ್ಚಿನ ವರ್ಗ "
                            f"{top_category}, ಅದರ ಮೊತ್ತ ₹{top_amount:,.2f}. "
                            f"ನಿಮ್ಮ ಒಟ್ಟು ಖರ್ಚು ₹{expenses:,.2f}."
                        )
                    else:
                        fallback = (
                            f"Your largest expense category is "
                            f"{top_category} at {money(top_amount)}. "
                            f"Total expenses are {money(expenses)}."
                        )

                elif (
                    "risk" in q
                    or "anomal" in q
                    or "ಅಪಾಯ" in q
                ):
                    if is_kannada:
                        fallback = (
                            f"ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಹಣಕಾಸಿನ ಅಪಾಯದ ಮಟ್ಟ "
                            f"{overall}. High-risk: {counts['High']}, "
                            f"Medium-risk: {counts['Medium']}, "
                            f"Low-risk: {counts['Low']}."
                        )
                    else:
                        fallback = (
                            f"Your current transaction risk level is {overall}. "
                            f"High-risk: {counts['High']}, "
                            f"Medium-risk: {counts['Medium']}, "
                            f"Low-risk: {counts['Low']}."
                        )

                elif (
                    "expense" in q
                    or "spend" in q
                    or "cost" in q
                    or "ಖರ್ಚು" in q
                ):
                    if is_kannada:
                        fallback = (
                            f"ನಿಮ್ಮ ಒಟ್ಟು ಖರ್ಚು ₹{expenses:,.2f}. "
                            f"ಇದು ನಿಮ್ಮ ಆದಾಯದ {ratio:.1f}% ಆಗಿದೆ. "
                            f"ಅತಿ ದೊಡ್ಡ ಖರ್ಚಿನ ವರ್ಗ {top_category}."
                        )
                    else:
                        fallback = (
                            f"Your total expenses are {money(expenses)}, "
                            f"equal to {ratio:.1f}% of income. "
                            f"The largest expense category is {top_category}."
                        )

                elif (
                    "profit" in q
                    or "margin" in q
                    or "ಲಾಭ" in q
                ):
                    if is_kannada:
                        fallback = (
                            f"ನಿಮ್ಮ ನಿವ್ವಳ ಲಾಭ ₹{profit:,.2f}. "
                            f"ಒಟ್ಟು ಆದಾಯ ₹{income:,.2f} ಮತ್ತು "
                            f"ಒಟ್ಟು ಖರ್ಚು ₹{expenses:,.2f}. "
                            f"ಲಾಭದ ಪ್ರಮಾಣ {margin:.1f}%."
                        )
                    else:
                        fallback = (
                            f"Your current net profit is {money(profit)} "
                            f"from income of {money(income)} and "
                            f"expenses of {money(expenses)}. "
                            f"Your profit margin is {margin:.1f}%."
                        )

                else:
                    if is_kannada:
                        fallback = (
                            f"ನಿಮ್ಮ ಒಟ್ಟು ಆದಾಯ ₹{income:,.2f}, "
                            f"ಒಟ್ಟು ಖರ್ಚು ₹{expenses:,.2f}, "
                            f"ನಿವ್ವಳ ಲಾಭ ₹{profit:,.2f} ಮತ್ತು "
                            f"ಲಾಭದ ಪ್ರಮಾಣ {margin:.1f}%."
                        )
                    else:
                        fallback = (
                            f"Based on your current MoneyFlow data: "
                            f"income is {money(income)}, expenses are "
                            f"{money(expenses)}, net profit is "
                            f"{money(profit)}, and profit margin is "
                            f"{margin:.1f}%."
                        )

                st.markdown(
                    f'<div class="insight-box">🧠 <b>'
                    f'{"CFO ಉತ್ತರ" if is_kannada else "CFO Analysis"}'
                    f'</b><br><br>{fallback}</div>',
                    unsafe_allow_html=True,
                )

def get_time_greeting():
    """Return a greeting based on the user's local time."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning 👋"
    if 12 <= hour < 17:
        return "Good afternoon 👋"
    if 17 <= hour < 22:
        return "Good evening 👋"
    return "Good night 👋"


def overview_page(df):
    page_header(
        get_time_greeting(),
        "Your financial command center — clear numbers, colourful insights and an AI CFO inside the dashboard.",
    )

    income, expenses, profit, margin, expense_ratio = financial_summary(df)

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            period = st.selectbox(
                "Period",
                ["All time", "This month", "Last 3 months", "Last 6 months"],
            )
        with c2:
            st.markdown(
                '<div style="padding-top:28px;color:#64748b;">Every chart is interactive — hover, click and explore the financial details.</div>',
                unsafe_allow_html=True,
            )

    filtered = df.copy()

    if not filtered.empty and period != "All time":
        latest_date = filtered["date"].max()
        if period == "This month":
            start = latest_date.replace(day=1)
        elif period == "Last 3 months":
            start = latest_date - pd.DateOffset(months=3)
        else:
            start = latest_date - pd.DateOffset(months=6)
        filtered = filtered[filtered["date"] >= start]

    fi, fe, fp, fm, fr = financial_summary(filtered)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Income", money(fi))
    k2.metric("💸 Total Expenses", money(fe))
    k3.metric("📈 Net Profit", money(fp))
    k4.metric("🎯 Profit Margin", percentage(fm))

    st.write("")

    # CHART 1 + CHART 2
    left, right = st.columns([1.55, 1])

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">📊 Income vs Expenses vs Profit</div>', unsafe_allow_html=True)
            monthly = monthly_data(filtered)

            if monthly.empty:
                st.info("Not enough data for a trend chart.")
            else:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=monthly["month"], y=monthly["Income"], name="Income",
                    marker_color="#4f46e5",
                    hovertemplate="Income: ₹%{y:,.0f}<extra></extra>",
                ))
                fig.add_trace(go.Bar(
                    x=monthly["month"], y=monthly["Expense"], name="Expenses",
                    marker_color="#f97316",
                    hovertemplate="Expenses: ₹%{y:,.0f}<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=monthly["month"], y=monthly["Profit"], name="Profit",
                    mode="lines+markers",
                    line=dict(color="#059669", width=4),
                    marker=dict(size=9),
                    hovertemplate="Profit: ₹%{y:,.0f}<extra></extra>",
                ))
                fig.update_layout(
                    barmode="group",
                    height=390,
                    font=dict(family="Times New Roman, Times, serif", color="#172033", size=13),
                    xaxis=dict(showgrid=False, title=None),
                    yaxis=dict(gridcolor="#e5e7eb", zeroline=False, title="Amount (₹)"),
                    margin=dict(l=10, r=10, t=25, b=10),
                    legend=dict(orientation="h"),
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, key="analytics_profit_trend")

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">🍩 Expense Breakdown</div>', unsafe_allow_html=True)
            category = (
                filtered[filtered["type"] == "Expense"]
                .groupby("category")["amount"]
                .sum()
                .reset_index()
                .sort_values("amount", ascending=False)
            )
            if category.empty:
                st.info("No expenses available.")
            else:
                fig = px.pie(
                    category,
                    names="category",
                    values="amount",
                    hole=.60,
                    color_discrete_sequence=[
                        "#4f46e5", "#0f766e", "#f97316", "#db2777",
                        "#0891b2", "#7c3aed", "#65a30d", "#dc2626"
                    ],
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="%{label}: ₹%{value:,.0f}<extra></extra>",
                )
                fig.update_layout(
                    height=390,
                    font=dict(family="Times New Roman, Times, serif", color="#172033", size=13),
                    margin=dict(l=5, r=5, t=20, b=10),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, key="overview_income_expense_profit")

                st.markdown(
                    '<div class="small-muted" style="margin-top:6px;">Hover over the chart for exact monthly values.</div>',
                    unsafe_allow_html=True,
                )

    # Financial health — no extra chart, keeps total charts to five.
    st.write("")
    h1, h2 = st.columns([1, 1.6])

    with h1:
        with st.container(border=True):
            st.markdown('<div class="section-title">💚 Financial Health</div>', unsafe_allow_html=True)

            # Do not assign a financial-health score before the user has
            # entered any transactions. A score such as 75/100 would be
            # misleading because it is not based on the user's data.
            if filtered.empty:
                health = None
                overall = "No data"

                st.markdown(
                    """
                    <div style="text-align:center;padding:12px;">
                        <div style="font-size:48px;font-weight:900;color:#64748b;">—/100</div>
                        <div style="font-size:16px;color:#64748b;">Overall financial health</div>
                        <div style="margin-top:12px;">
                            <span style="background:#f1f5f9;color:#475569;padding:7px 12px;border-radius:999px;font-weight:800;">
                                No financial data yet
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(0.0)
                st.write("Profit margin: **—**")
                st.write("Expense ratio: **—**")
                st.caption("Add your first transaction to calculate financial health.")
            else:
                health = 50
                if fm >= 50:
                    health += 25
                elif fm >= 30:
                    health += 15
                elif fm >= 15:
                    health += 8

                if fr <= 40:
                    health += 15
                elif fr <= 60:
                    health += 8

                _, _, overall = risk_analysis(filtered)
                if overall == "Low":
                    health += 10
                elif overall == "Medium":
                    health += 5

                health = min(100, max(0, int(health)))

                st.markdown(
                    f"""
                    <div style="text-align:center;padding:12px;">
                        <div style="font-size:48px;font-weight:900;color:#4f46e5;">{health}/100</div>
                        <div style="font-size:16px;color:#64748b;">Overall financial health</div>
                        <div style="margin-top:12px;">
                            <span style="background:#dcfce7;color:#166534;padding:7px 12px;border-radius:999px;font-weight:800;">
                                Risk: {overall}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.progress(health / 100)
                st.write(f"Profit margin: **{fm:.1f}%**")
                st.write(f"Expense ratio: **{fr:.1f}%**")

    with h2:
        with st.container(border=True):
            st.markdown('<div class="section-title">💡 CFO Insights</div>', unsafe_allow_html=True)
            for insight in build_insights(filtered):
                st.markdown(
                    f'<div class="insight-box">💡 {insight}</div>',
                    unsafe_allow_html=True,
                )

    # AI CFO INSIDE THE DASHBOARD
    st.write("")
    with st.container(border=True):
        cfo_inside_dashboard(filtered)

    # Recent transactions
    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">🧾 Recent Transactions</div>', unsafe_allow_html=True)
        recent = filtered.sort_values("date", ascending=False).head(8).copy()

        if recent.empty:
            st.info("No transactions available.")
        else:
            display = recent[["date", "description", "category", "type", "amount"]].copy()
            display["date"] = pd.to_datetime(display["date"], errors="coerce")
            display["date"] = display["date"].dt.strftime("%d %b %Y")
            display["amount"] = display["amount"].map(money)
            st.dataframe(display, use_container_width=True, hide_index=True)


# ============================================================
# TRANSACTIONS
# ============================================================

def transactions_page(df):
    page_header(
        "Transactions",
        "Search, filter, add and inspect your financial transactions.",
    )

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            search = st.text_input("🔎 Search", placeholder="Description or category")

        with c2:
            types = st.multiselect(
                "Type",
                ["Income", "Expense"],
                default=["Income", "Expense"],
            )

        with c3:
            categories = sorted(df["category"].dropna().unique().tolist())
            selected_categories = st.multiselect(
                "Category",
                categories,
            )

    filtered = df.copy()

    if search:
        text = (
            filtered["description"].str.contains(search, case=False, na=False)
            | filtered["category"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[text]

    if types:
        filtered = filtered[filtered["type"].isin(types)]

    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]

    st.write(f"Showing **{len(filtered)}** transaction(s)")

    with st.container(border=True):
        table = filtered.copy()
        table["date"] = pd.to_datetime(table["date"], errors="coerce")
        table["date"] = table["date"].dt.strftime("%Y-%m-%d")
        table["amount"] = table["amount"].map(money)

        st.dataframe(
            table[
                ["id", "date", "description", "category", "type", "amount"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.write("")

    add_col, detail_col = st.columns(2)

    with add_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">Add Transaction</div>', unsafe_allow_html=True)

            with st.form("add_transaction"):
                date = st.date_input("Date", datetime.now().date())
                description = st.text_input("Description")
                category = st.text_input("Category")
                transaction_type = st.selectbox("Type", ["Income", "Expense"])
                amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)

                submitted = st.form_submit_button(
                    "Save Transaction",
                    use_container_width=True,
                    type="primary",
                )

                if submitted:
                    if not description or not category:
                        st.error("Description and category are required.")
                    else:
                        existing_ids = pd.to_numeric(df["id"], errors="coerce").dropna()
                        new_id = int(existing_ids.max()) + 1 if not existing_ids.empty else 1

                        new_row = pd.DataFrame(
                            [{
                                "id": new_id,
                                "date": pd.Timestamp(date),
                                "description": description,
                                "category": category,
                                "type": transaction_type,
                                "amount": amount,
                            }]
                        )

                        updated = pd.concat([df, new_row], ignore_index=True)
                        save_transactions(updated)

                        st.success("Transaction saved.")
                        st.rerun()

    with detail_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">Transaction Drill-down</div>', unsafe_allow_html=True)

            if filtered.empty:
                st.info("No transaction available.")
            else:
                selected_id = st.selectbox(
                    "Select transaction",
                    filtered["id"].tolist(),
                )

                row = filtered[filtered["id"] == selected_id].iloc[0]

                st.write(f"**Description:** {row['description']}")
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Type:** {row['type']}")
                st.write(f"**Date:** {row['date'].strftime('%d %B %Y')}")
                st.write(f"**Amount:** {money(row['amount'])}")


# ============================================================


# DATA IMPORT
# ============================================================

def _read_pdf_dataset(uploaded_file):
    """Read a structured table from a PDF using pdfplumber when available."""
    try:
        import pdfplumber
    except ImportError as exc:
        raise ImportError(
            "PDF support needs pdfplumber. Run: pip install pdfplumber"
        ) from exc

    rows = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                cleaned = []
                for row in table:
                    if row:
                        cleaned.append([
                            "" if value is None else str(value).strip()
                            for value in row
                    ])

                if len(cleaned) < 2:
                    continue

                header = [str(x).strip() for x in cleaned[0]]
                body = cleaned[1:]

                # Keep the table with the strongest financial column match.
                header_text = " ".join(header).lower()
                score = sum(
                    key in header_text
                    for key in ["date", "description", "category", "type", "amount"]
                )

                if score >= 2:
                    rows.append((score, header, body))

    if not rows:
        raise ValueError(
            "No structured financial table was found in this PDF. "
            "For the most reliable import, use an Excel or CSV file."
        )

    rows.sort(key=lambda item: item[0], reverse=True)
    _, header, body = rows[0]

    width = len(header)
    body = [
        row[:width] + [""] * max(0, width - len(row))
        for row in body
    ]

    return pd.DataFrame(body, columns=header)


def data_import_page():
    page_header(
        "Data Import",
        "Upload, combine, switch and remove your financial datasets.",
    )

    identifier = st.session_state.get("user_email", "")
    datasets = _ensure_dataset_registry(identifier)

    # ------------------------------------------------------------
    # Dataset manager
    # ------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<div class="section-title">📚 My Financial Datasets</div>', unsafe_allow_html=True)

        if not datasets:
            st.info("No dataset exists yet. Upload your first financial dataset below.")
        else:
            labels = []
            for item in datasets:
                cats = ", ".join(item.get("categories", [])) or "No categories"
                labels.append(f"{item.get('name', 'Dataset')} • {item.get('rows', 0)} rows • {cats}")

            current_id = _active_dataset_id(identifier)
            current_index = next((i for i, item in enumerate(datasets) if item.get("id") == current_id), 0)
            selected_label = st.selectbox(
                "Active dataset",
                labels,
                index=current_index,
                key="active_dataset_selector",
            )
            selected_index = labels.index(selected_label)
            selected_id = datasets[selected_index]["id"]

            if selected_id != current_id:
                _set_active_dataset(selected_id)
                st.rerun()

            current = datasets[selected_index]
            st.caption(
                f"Active: **{current.get('name', 'Dataset')}**  |  "
                f"Categories: {', '.join(current.get('categories', [])) or 'None'}  |  "
                f"Rows: {current.get('rows', 0)}"
            )

            delete_col, clear_col = st.columns(2)
            with delete_col:
                if st.button("🗑️ Remove this dataset", key="remove_active_dataset", type="secondary"):
                    st.session_state["confirm_delete_dataset"] = selected_id
                    st.rerun()
            with clear_col:
                if st.button("🧹 Clear all my datasets", key="clear_all_datasets", type="secondary"):
                    st.session_state["confirm_clear_datasets"] = True
                    st.rerun()

            if st.session_state.get("confirm_delete_dataset") == selected_id:
                st.warning(f"Delete **{current.get('name', 'this dataset')}** permanently?")
                yes, no = st.columns(2)
                with yes:
                    if st.button("Yes, delete", key="confirm_delete_yes", type="primary"):
                        path = _dataset_file(selected_id, identifier)
                        if path.exists():
                            path.unlink()
                        datasets = [x for x in _read_datasets(identifier) if x.get("id") != selected_id]
                        _write_datasets(datasets, identifier)
                        st.session_state.pop("confirm_delete_dataset", None)
                        if datasets:
                            st.session_state.active_dataset_id = datasets[0]["id"]
                        else:
                            st.session_state.pop("active_dataset_id", None)
                        st.success("Dataset removed.")
                        st.rerun()
                with no:
                    if st.button("Cancel", key="confirm_delete_no"):
                        st.session_state.pop("confirm_delete_dataset", None)
                        st.rerun()

            if st.session_state.get("confirm_clear_datasets"):
                st.warning("This will permanently remove ALL your financial datasets on this account.")
                yes, no = st.columns(2)
                with yes:
                    if st.button("Yes, clear everything", key="confirm_clear_yes", type="primary"):
                        for item in _read_datasets(identifier):
                            path = _dataset_file(item.get("id"), identifier)
                            if path.exists():
                                path.unlink()
                        _write_datasets([], identifier)
                        legacy = _user_transactions_file(identifier)
                        if legacy.exists():
                            legacy.unlink()
                        st.session_state.pop("active_dataset_id", None)
                        st.session_state.pop("confirm_clear_datasets", None)
                        st.success("All financial datasets removed.")
                        st.rerun()
                with no:
                    if st.button("Cancel", key="confirm_clear_no"):
                        st.session_state.pop("confirm_clear_datasets", None)
                        st.rerun()

    # ------------------------------------------------------------
    # Upload / validate / smart combine
    # ------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<div class="section-title">1. Upload Financial Dataset</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Choose a financial dataset or receipt photo",
            type=[
                "xlsx",
                "xls",
                "csv",
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            help=(
                "Upload CSV, Excel or PDF financial datasets, "
                "or JPG/JPEG/PNG/WEBP receipt photos."
            ),
            key="financial_dataset_uploader",
        )

        if uploaded:
            st.success(f"Uploaded: {uploaded.name}")
            suffix = Path(uploaded.name).suffix.lower()

            # --------------------------------------------------------
            # RECEIPT PHOTO
            # --------------------------------------------------------
            if suffix in [".jpg", ".jpeg", ".png", ".webp"]:
                st.markdown("### 📷 Receipt Photo")
                st.image(
                    uploaded,
                    caption=uploaded.name,
                    use_container_width=True,
                )

                st.info(
                    "MoneyFlow can read this receipt photo with AI and "
                    "turn the extracted total into an expense transaction."
                )

                if st.button(
                    "🤖 Analyze Receipt with AI",
                    type="primary",
                    use_container_width=True,
                    key="analyze_receipt_photo",
                ):
                    try:
                        upload_dir = DATA_DIR / "raw_receipts"
                        upload_dir.mkdir(parents=True, exist_ok=True)

                        safe_name = (
                            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                            f"{Path(uploaded.name).name}"
                        )
                        file_path = upload_dir / safe_name

                        with open(file_path, "wb") as file:
                            file.write(uploaded.getbuffer())

                        from src.document_analyzer import analyze_document

                        with st.spinner("🤖 AI is analyzing the receipt..."):
                            result = analyze_document(str(file_path))

                        if not isinstance(result, dict):
                            raise ValueError(
                                "AI returned an invalid receipt response."
                            )

                        st.session_state["receipt_analysis"] = result
                        st.session_state["receipt_filename"] = uploaded.name
                        st.session_state["receipt_file_path"] = str(file_path)

                    except Exception as error:
                        st.error(
                            f"Could not analyze the receipt: {error}"
                        )

            # --------------------------------------------------------
            # NORMAL FINANCIAL DATASET
            # --------------------------------------------------------
            else:
                try:
                    if suffix == ".csv":
                        imported_df = pd.read_csv(uploaded)
                    elif suffix in [".xlsx", ".xls"]:
                        imported_df = pd.read_excel(uploaded)
                    elif suffix == ".pdf":
                        imported_df = _read_pdf_dataset(uploaded)
                    else:
                        imported_df = None

                    if imported_df is not None:
                        st.session_state["imported_dataset"] = imported_df.copy()
                        st.session_state["imported_filename"] = uploaded.name
                except Exception as error:
                    st.error(f"Could not read the dataset: {error}")

    # ================================================================
    # RECEIPT ANALYSIS RESULT
    # ================================================================

    receipt_result = st.session_state.get("receipt_analysis")

    if receipt_result is not None:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">2. Verify Receipt Details</div>',
                unsafe_allow_html=True,
            )

            st.success(
                "✅ Receipt analyzed. Please verify the extracted values before saving."
            )

            left, right = st.columns(2)

            with left:
                receipt_vendor = st.text_input(
                    "Vendor / Store",
                    value=str(receipt_result.get("vendor") or ""),
                    key="receipt_vendor",
                )

                receipt_date = st.text_input(
                    "Date",
                    value=str(receipt_result.get("date") or ""),
                    key="receipt_date",
                )

                receipt_category = st.text_input(
                    "Category",
                    value=str(
                        receipt_result.get("category") or "Other"
                    ),
                    key="receipt_category",
                )

                receipt_payment = st.text_input(
                    "Payment Method",
                    value=str(
                        receipt_result.get("payment_method") or ""
                    ),
                    key="receipt_payment_method",
                )

            with right:
                receipt_invoice = st.text_input(
                    "Invoice Number",
                    value=str(
                        receipt_result.get("invoice_number") or ""
                    ),
                    key="receipt_invoice_number",
                )

                receipt_subtotal = st.number_input(
                    "Subtotal",
                    min_value=0.0,
                    value=float(receipt_result.get("subtotal") or 0),
                    step=1.0,
                    key="receipt_subtotal",
                )

                receipt_tax = st.number_input(
                    "Tax / GST",
                    min_value=0.0,
                    value=float(receipt_result.get("tax") or 0),
                    step=1.0,
                    key="receipt_tax",
                )

                receipt_total = st.number_input(
                    "Final Total",
                    min_value=0.0,
                    value=float(receipt_result.get("total") or 0),
                    step=1.0,
                    key="receipt_total",
                )

            receipt_notes = st.text_area(
                "Notes",
                value=str(receipt_result.get("notes") or ""),
                key="receipt_notes",
            )

            confidence = receipt_result.get("confidence")
            if confidence is not None:
                try:
                    confidence_value = float(confidence)
                    if confidence_value <= 1:
                        confidence_value *= 100
                    st.metric(
                        "AI Confidence",
                        f"{confidence_value:.1f}%",
                    )
                except Exception:
                    pass

            st.markdown("### 🛒 Extracted Items")

            items = receipt_result.get("items") or []
            if items:
                st.dataframe(
                    pd.DataFrame(items),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No individual items were detected.")

            st.warning(
                "Verify the extracted information before saving it."
            )

            save_col, remove_col = st.columns(2)

            with save_col:
                if st.button(
                    "💾 Save Receipt as Expense",
                    type="primary",
                    use_container_width=True,
                    key="save_receipt_as_expense",
                ):
                    if receipt_total <= 0:
                        st.error(
                            "Final total must be greater than zero."
                        )
                    else:
                        try:
                            parsed_date = pd.to_datetime(
                                receipt_date,
                                errors="coerce",
                            )

                            if pd.isna(parsed_date):
                                parsed_date = pd.Timestamp.now()

                            current_df = load_transactions()

                            if current_df.empty:
                                next_id = 1
                            else:
                                ids = pd.to_numeric(
                                    current_df["id"],
                                    errors="coerce",
                                )
                                next_id = (
                                    int(ids.max()) + 1
                                    if ids.notna().any()
                                    else len(current_df) + 1
                                )

                            new_row = pd.DataFrame(
                                [{
                                    "id": next_id,
                                    "date": parsed_date,
                                    "description": (
                                        receipt_vendor.strip()
                                        or "Receipt Expense"
                                    ),
                                    "category": (
                                        receipt_category.strip()
                                        or "Other"
                                    ),
                                    "type": "Expense",
                                    "amount": float(receipt_total),
                                }]
                            )

                            combined_df = pd.concat(
                                [current_df, new_row],
                                ignore_index=True,
                            )

                            save_transactions(combined_df)

                            st.session_state.pop(
                                "receipt_analysis",
                                None,
                            )
                            st.session_state.pop(
                                "receipt_filename",
                                None,
                            )
                            st.session_state.pop(
                                "receipt_file_path",
                                None,
                            )

                            st.success(
                                "✅ Receipt saved as an expense transaction."
                            )
                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"Could not save receipt: {error}"
                            )

            with remove_col:
                if st.button(
                    "✖ Remove Receipt",
                    use_container_width=True,
                    key="remove_receipt_analysis",
                ):
                    st.session_state.pop(
                        "receipt_analysis",
                        None,
                    )
                    st.session_state.pop(
                        "receipt_filename",
                        None,
                    )
                    st.session_state.pop(
                        "receipt_file_path",
                        None,
                    )
                    st.rerun()

    # ================================================================
    # NORMAL DATASET PREVIEW / VALIDATION
    # ================================================================

    imported_df = st.session_state.get("imported_dataset")

    if imported_df is not None:
        with st.container(border=True):
            st.markdown('<div class="section-title">3. Preview & Validate Dataset</div>', unsafe_allow_html=True)
            st.dataframe(imported_df, use_container_width=True, height=300, hide_index=True)

            normalized = imported_df.copy()
            normalized.columns = [str(column).strip().lower().replace(" ", "_") for column in normalized.columns]
            rename_map = {}
            for column in normalized.columns:
                compact = column.replace("_", "")
                if compact in ["transactiondate", "transaction_date"]:
                    rename_map[column] = "date"
                elif compact in ["details", "description", "particulars", "narration"]:
                    rename_map[column] = "description"
                elif compact in ["expensecategory", "category"]:
                    rename_map[column] = "category"
                elif compact in ["transactiontype", "type"]:
                    rename_map[column] = "type"
                elif compact in ["value", "amount", "transactionamount"]:
                    rename_map[column] = "amount"
            normalized = normalized.rename(columns=rename_map)

            required = {"date", "description", "category", "type", "amount"}
            missing = required - set(normalized.columns)
            if missing:
                st.error("Missing required columns: " + ", ".join(sorted(missing)) + ".")
            else:
                normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
                normalized["amount"] = pd.to_numeric(
                    normalized["amount"].astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False).str.replace("Rs.", "", regex=False).str.strip(),
                    errors="coerce",
                )
                normalized["type"] = normalized["type"].astype(str).str.strip().str.title()
                normalized["category"] = normalized["category"].astype(str).str.strip()

                invalid_dates = int(normalized["date"].isna().sum())
                invalid_amounts = int(normalized["amount"].isna().sum())
                invalid_types = int((~normalized["type"].isin(["Income", "Expense"])).sum())

                a, b, c, d = st.columns(4)
                a.metric("Rows", len(normalized))
                b.metric("Invalid", invalid_dates + invalid_amounts + invalid_types)
                c.metric("Duplicates", int(normalized.duplicated().sum()))
                d.metric("Valid", max(0, len(normalized) - invalid_dates - invalid_amounts - invalid_types))

                clean = normalized.dropna(subset=["date", "description", "category", "type", "amount"]).copy()
                clean = clean[clean["type"].isin(["Income", "Expense"])].copy()
                clean["amount"] = clean["amount"].abs()
                clean = clean.drop_duplicates(subset=["date", "description", "category", "type", "amount"]).copy()
                clean = clean[["date", "description", "category", "type", "amount"]]
                incoming_categories = _dataset_categories(clean)

                st.write("")
                st.markdown("**Dataset matching**")
                if not incoming_categories:
                    st.warning("No valid categories were found in this dataset.")
                else:
                    st.write("Incoming categories: " + ", ".join(incoming_categories))
                    matches = [
                        item for item in _read_datasets(identifier)
                        if item.get("categories", []) == incoming_categories
                    ]
                    if matches:
                        st.success(
                            f"Matching categories found in {matches[0].get('name', 'an existing dataset')}. "
                            "This upload will be combined with that dataset."
                        )
                    else:
                        st.info("No dataset has exactly these categories. A new separate dataset will be created.")

                if st.button("📥 Add Dataset", type="primary", use_container_width=True, key="smart_add_dataset"):
                    if clean.empty:
                        st.error("There are no valid transactions to add.")
                    else:
                        datasets = _read_datasets(identifier)
                        matches = [item for item in datasets if item.get("categories", []) == incoming_categories]
                        if matches:
                            target = matches[0]
                            combined = _merge_into_dataset(target["id"], clean, identifier)
                            for item in datasets:
                                if item.get("id") == target["id"]:
                                    item["categories"] = _dataset_categories(combined)
                                    item["rows"] = int(len(combined))
                            _write_datasets(datasets, identifier)
                            st.session_state.active_dataset_id = target["id"]
                            message = f"Added {len(clean)} rows to {target.get('name', 'the matching dataset')}."
                        else:
                            new_id = _create_dataset(clean, st.session_state.get("imported_filename", "Dataset"), identifier)
                            st.session_state.active_dataset_id = new_id
                            message = "Categories were different, so a new separate dataset was created."

                        st.session_state["imported_dataset"] = None
                        st.session_state.pop("imported_filename", None)
                        st.success(message)
                        st.rerun()

                if st.button("✖ Remove uploaded file", key="remove_uploaded_dataset"):
                    st.session_state.pop("imported_dataset", None)
                    st.session_state.pop("imported_filename", None)
                    st.rerun()

    with st.container(border=True):
        st.markdown('<div class="section-title">4. Current Dataset</div>', unsafe_allow_html=True)
        current = load_transactions()
        datasets = _read_datasets(identifier)
        active = next((x for x in datasets if x.get("id") == _active_dataset_id(identifier)), None)
        if active:
            st.write(f"**{active.get('name', 'Dataset')}** — {len(current)} transactions")
            st.dataframe(current.tail(10), use_container_width=True, hide_index=True)
        else:
            st.info("No dataset selected. Upload a dataset to get started.")


# ============================================================
# ANALYTICS
# ============================================================

def analytics_page(df):
    page_header(
        "Analytics",
        "Explore income, expenses, profit and category-level financial behavior.",
    )

    income, expenses, profit, margin, ratio = financial_summary(df)

    a, b, c, d = st.columns(4)
    a.metric("Income", money(income))
    b.metric("Expenses", money(expenses))
    c.metric("Profit", money(profit))
    d.metric("Expense Ratio", percentage(ratio))

    st.write("")

    monthly = monthly_data(df)

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Profit Trend</div>', unsafe_allow_html=True)

            if not monthly.empty:
                fig = px.line(
                    monthly,
                    x="month",
                    y="Profit",
                    markers=True,
                )
                fig.update_layout(
                    height=350,
                    font=dict(family="Times New Roman, Times, serif", color="#172033", size=13),
                    margin=dict(l=10, r=10, t=20, b=10),
                    yaxis_title="Profit (₹)",
                    xaxis_title=None,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Expense Categories</div>', unsafe_allow_html=True)

            category = (
                df[df["type"] == "Expense"]
                .groupby("category")["amount"]
                .sum()
                .reset_index()
                .sort_values("amount", ascending=False)
            )

            if not category.empty:
                fig = px.bar(
                    category,
                    x="amount",
                    y="category",
                    orientation="h",
                )
                fig.update_layout(
                    height=350,
                    font=dict(family="Times New Roman, Times, serif", color="#172033", size=13),
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="Amount (₹)",
                    yaxis_title=None,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, key="analytics_expense_categories")

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="section-title">Monthly Financial Table</div>', unsafe_allow_html=True)

        if monthly.empty:
            st.info("No monthly data available.")
        else:
            table = monthly.copy()
            for col in ["Income", "Expense", "Profit"]:
                table[col] = table[col].map(money)

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# FORECAST
# ============================================================

def forecast_page():
    page_header(
        "Forecast",
        "Generate a next-month forecast from your own MoneyFlow transactions.",
    )

    # Never display the global/demo historical CSV to users.
    # A new account must start with a completely empty workspace.
    user_df = load_transactions()

    if user_df.empty:
        with st.container(border=True):
            st.markdown('<div class="section-title">📈 Your Forecast</div>', unsafe_allow_html=True)
            st.info("No financial data yet. Add transactions or upload a receipt to generate your first forecast.")
        return

    monthly = monthly_data(user_df)
    if len(monthly) < 3:
        with st.container(border=True):
            st.markdown('<div class="section-title">📈 Your Forecast</div>', unsafe_allow_html=True)
            st.info("Add transactions covering at least 3 months to generate a meaningful forecast.")
        return

    history = monthly.rename(columns={"month": "month", "Income": "income", "Expense": "expenses"})[["month", "income", "expenses", "Profit"]].copy()
    history["month"] = pd.to_datetime(history["month"] + "-01", errors="coerce")
    history = history.rename(columns={"Profit": "profit"}).dropna().reset_index(drop=True)

    with st.container(border=True):
        st.markdown('<div class="section-title">📊 Your Historical Financial Data</div>', unsafe_allow_html=True)
        display = history.assign(
            month=history["month"].dt.strftime("%b %Y"),
            income=history["income"].map(money),
            expenses=history["expenses"].map(money),
            profit=history["profit"].map(money),
        )
        st.dataframe(display, width="stretch", hide_index=True)

    try:
        from xgboost import XGBRegressor

        data = history.copy()
        data["year"] = data["month"].dt.year
        data["month_number"] = data["month"].dt.month
        data["income_lag_1"] = data["income"].shift(1)
        data["expenses_lag_1"] = data["expenses"].shift(1)
        data["profit_lag_1"] = data["profit"].shift(1)
        train = data.dropna().copy()

        if len(train) < 2:
            st.info("Add more monthly transaction data before forecasting.")
            return

        features = ["year", "month_number", "income_lag_1", "expenses_lag_1", "profit_lag_1"]
        models = {}
        for target in ["income", "expenses"]:
            model = XGBRegressor(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.05,
                objective="reg:squarederror",
                random_state=42,
            )
            model.fit(train[features], train[target])
            models[target] = model

        latest = data.iloc[-1]
        next_month = latest["month"] + pd.DateOffset(months=1)
        future = pd.DataFrame([{
            "year": next_month.year,
            "month_number": next_month.month,
            "income_lag_1": latest["income"],
            "expenses_lag_1": latest["expenses"],
            "profit_lag_1": latest["profit"],
        }])

        predicted_income = max(0, float(models["income"].predict(future)[0]))
        predicted_expenses = max(0, float(models["expenses"].predict(future)[0]))
        predicted_profit = predicted_income - predicted_expenses

        p1, p2, p3 = st.columns(3)
        p1.metric(f"Predicted Income · {next_month.strftime('%b %Y')}", money(predicted_income))
        p2.metric("Predicted Expenses", money(predicted_expenses))
        p3.metric("Predicted Profit", money(predicted_profit))

        with st.container(border=True):
            st.markdown('<div class="section-title">Forecast Interpretation</div>', unsafe_allow_html=True)
            forecast_margin = (predicted_profit / predicted_income * 100) if predicted_income else 0
            st.markdown(
                f'<div class="insight-box">📈 For {next_month.strftime("%B %Y")}, MoneyFlow predicts '
                f'<b>{money(predicted_income)}</b> income, <b>{money(predicted_expenses)}</b> expenses and '
                f'<b>{money(predicted_profit)}</b> profit, implying a predicted profit margin of '
                f'<b>{forecast_margin:.1f}%</b>.</div>',
                unsafe_allow_html=True,
            )
            st.caption("Forecast is calculated from the signed-in user's own transaction history. It is an estimate, not a guaranteed financial result.")

    except Exception as error:
        st.error(f"Forecast model could not run: {error}")


# ============================================================
# RISK & ANOMALIES
# ============================================================

def risk_page(df):
    page_header(
        "Risk & Anomalies",
        "Identify unusually large expenses and understand transaction risk.",
    )

    work = df.copy()
    required = ["date", "description", "category", "type", "amount"]
    for col in required:
        if col not in work.columns:
            work[col] = pd.Series(dtype="object")

    if work.empty:
        risk_df = work.copy()
        risk_df["risk_level"] = pd.Series(dtype="object")
        counts = {"High": 0, "Medium": 0, "Low": 0}
        overall = "Low"
    else:
        work["date"] = pd.to_datetime(work["date"], errors="coerce")
        work["amount"] = pd.to_numeric(work["amount"], errors="coerce")
        work["type"] = work["type"].astype(str).str.strip().str.title()
        work = work.dropna(subset=["amount"])
        work = work[work["amount"] > 0].copy()
        risk_df, counts, overall = risk_analysis(work)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Overall Risk", overall)
    r2.metric("🔴 High", counts.get("High", 0))
    r3.metric("🟠 Medium", counts.get("Medium", 0))
    r4.metric("🟢 Low", counts.get("Low", 0))

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
        if work.empty:
            st.info("Add expense transactions to see risk distribution.")
        else:
            chart_df = pd.DataFrame({
                "Risk": ["High", "Medium", "Low"],
                "Count": [int(counts.get("High", 0)), int(counts.get("Medium", 0)), int(counts.get("Low", 0))],
            }).set_index("Risk")
            # Native Streamlit chart avoids the browser freeze caused by the Plotly risk chart.
            st.bar_chart(chart_df, height=300, width="stretch")

    with st.container(border=True):
        st.markdown('<div class="section-title">Flagged Transactions</div>', unsafe_allow_html=True)
        if risk_df.empty:
            st.info("No expense transactions available.")
        else:
            flagged = risk_df[risk_df["risk_level"].isin(["High", "Medium"])].copy()
            if flagged.empty:
                st.success("No medium/high-risk transactions detected.")
            else:
                flagged["date"] = pd.to_datetime(flagged["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                flagged["amount"] = flagged["amount"].map(money)
                st.dataframe(
                    flagged[["date", "description", "category", "amount", "risk_level"]],
                    width="stretch",
                    hide_index=True,
                )


# ============================================================
# PROFILE
# ============================================================

def profile_page():
    page_header(
        "Profile",
        "Manage your personal MoneyFlow profile.",
    )

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "full_name": st.session_state.user_name or "MoneyFlow User",
            "email": st.session_state.user_email or "",
            "phone": "",
            "dob": None,
            "photo": None,
        }

    profile = st.session_state.profile

    # Keep the profile content left-aligned and spacious.
    with st.container(border=True):
        st.markdown('<div class="section-title">👤 Personal Information</div>', unsafe_allow_html=True)

        left, right = st.columns([1, 2.5])

        with left:
            if profile.get("photo"):
                st.image(profile["photo"], width=140)
            else:
                st.markdown(
                    '<div style="width:140px;height:140px;border-radius:50%;background:linear-gradient(135deg,#4f46e5,#0f766e);display:flex;align-items:center;justify-content:center;color:white;font-size:48px;font-weight:900;">MF</div>',
                    unsafe_allow_html=True,
                )

            uploaded_photo = st.file_uploader(
                "Upload Profile Picture",
                type=["png", "jpg", "jpeg", "webp"],
                key="profile_photo_upload",
                help="Choose a profile picture from your device.",
            )

            if uploaded_photo is not None:
                profile["photo"] = uploaded_photo
                st.session_state.profile = profile
                st.image(uploaded_photo, width=140)
                st.success("Profile picture selected.")

        with right:
            full_name = st.text_input(
                "Full Name",
                value=profile["full_name"],
                key="profile_full_name",
            )
            email = st.text_input(
                "Email",
                value=profile["email"],
                key="profile_email",
            )
            phone = st.text_input(
                "Phone Number",
                value=profile["phone"],
                placeholder="+91 XXXXX XXXXX",
                key="profile_phone",
            )
            dob = st.date_input(
                "Date of Birth",
                value=profile["dob"],
                min_value=datetime(1900, 1, 1).date(),
                key="profile_dob",
            )

        if st.button("Save Profile", use_container_width=True, type="primary", key="save_profile"):
            st.session_state.profile = {
                "full_name": full_name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "dob": dob,
                "photo": profile.get("photo"),
            }
            st.session_state.user_name = full_name.strip() or "MoneyFlow User"
            st.session_state.user_email = email.strip() or phone.strip()
            st.success("Profile updated successfully.")
            st.rerun()


# ============================================================
# SETTINGS
# ============================================================

def settings_page():
    page_header("Settings", "Customize how MoneyFlow works for you.")

    if "settings" not in st.session_state:
        st.session_state.settings = {
            "theme": "Light",
            "currency": "INR (₹)",
            "date_format": "DD-MM-YYYY",
            "financial_alerts": True,
            "risk_alerts": True,
            "forecast_alerts": True,
            "ai_alerts": True,
            "biometric": False,
            "remember_device": True,
            "ai_suggestions": True,
            "automatic_explanations": True,
            "forecast_insights": True,
        }

    cfg = st.session_state.settings

    with st.container(border=True):
        st.markdown('<div class="section-title">🎨 Appearance</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("Theme", ["Light", "Dark", "System default"], index=["Light","Dark","System default"].index(cfg["theme"]), key="settings_theme")
        with col2:
            currency = st.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)"], index=["INR (₹)","USD ($)","EUR (€)"].index(cfg["currency"]), key="settings_currency")
        date_format = st.selectbox("Date format", ["DD-MM-YYYY", "YYYY-MM-DD", "MM-DD-YYYY"], index=["DD-MM-YYYY","YYYY-MM-DD","MM-DD-YYYY"].index(cfg["date_format"]), key="settings_date_format")
        if st.button("Apply Theme", use_container_width=True, key="apply_theme"):
            cfg["theme"] = theme
            st.session_state.settings = cfg
            st.rerun()

    with st.container(border=True):
        st.markdown('<div class="section-title">🔔 Notifications</div>', unsafe_allow_html=True)
        financial_alerts = st.toggle("Financial Alerts", value=cfg["financial_alerts"], key="settings_financial_alerts")
        risk_alerts = st.toggle("Risk & Anomaly Alerts", value=cfg["risk_alerts"], key="settings_risk_alerts")
        forecast_alerts = st.toggle("Forecast Alerts", value=cfg["forecast_alerts"], key="settings_forecast_alerts")
        ai_alerts = st.toggle("AI CFO Alerts", value=cfg["ai_alerts"], key="settings_ai_alerts")

    with st.container(border=True):
        st.markdown('<div class="section-title">🔐 Login & Security</div>', unsafe_allow_html=True)
        biometric = st.toggle("Biometric Login", value=cfg["biometric"], key="settings_biometric", help="Fingerprint or Face ID can be connected when the MoneyFlow mobile app uses device authentication.")
        remember_device = st.toggle("Remember This Device", value=cfg["remember_device"], key="settings_remember")
        st.info("Fingerprint / Face ID is a mobile-device feature. This Streamlit version only stores your preference; it does not pretend to perform biometric verification.")
        st.markdown(f'<div class="data-source-card"><div class="data-source-label">ACTIVE SESSION</div><div class="data-source-value">{st.session_state.user_email or "Current device"}</div></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-title">🤖 AI CFO Preferences</div>', unsafe_allow_html=True)
        ai_suggestions = st.toggle("AI Suggestions", value=cfg["ai_suggestions"], key="settings_ai_suggestions")
        automatic_explanations = st.toggle("Automatic Explanations", value=cfg["automatic_explanations"], key="settings_auto_explanations")
        forecast_insights = st.toggle("Forecast Insights", value=cfg["forecast_insights"], key="settings_forecast_insights")

    if st.button("Save Settings", use_container_width=True, type="primary", key="save_settings"):
        st.session_state.settings = {
            "theme": theme,
            "currency": currency,
            "date_format": date_format,
            "financial_alerts": financial_alerts,
            "risk_alerts": risk_alerts,
            "forecast_alerts": forecast_alerts,
            "ai_alerts": ai_alerts,
            "biometric": biometric,
            "remember_device": remember_device,
            "ai_suggestions": ai_suggestions,
            "automatic_explanations": automatic_explanations,
            "forecast_insights": forecast_insights,
        }
        st.success("Settings saved successfully.")


# ============================================================
# ROUTER
# ============================================================

def main_app():
    df = load_transactions()

    selected = sidebar()

    if selected == "🏠  Overview":
        overview_page(df)

    elif selected == "💳  Transactions":
        transactions_page(df)

    elif selected == "📂  Data Import":
        data_import_page()

    elif selected == "📊  Analytics":
        analytics_page(df)

    elif selected == "📈  Forecast":
        forecast_page()

    elif selected == "🚨  Risk & Anomalies":
        risk_page(df)

    elif selected == "👤  Profile":
        profile_page()

    elif selected == "⚙️  Settings":
        settings_page()


# ============================================================
# APP START
# ============================================================

if not st.session_state.logged_in:
    login_page()
else:
    main_app()




import os
import hashlib
import hmac
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# MONEYFLOW - END-TO-END STREAMLIT DASHBOARD
# ============================================================

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

# Demo credentials are kept for the current Streamlit session so that
# the same email/phone cannot be opened with a different password.
if "demo_users" not in st.session_state:
    st.session_state.demo_users = {}

if "selected_transaction" not in st.session_state:
    st.session_state.selected_transaction = None

if "settings" not in st.session_state:
    st.session_state.settings = {"theme":"Light","currency":"INR (₹)","date_format":"DD-MM-YYYY","financial_alerts":True,"risk_alerts":True,"forecast_alerts":True,"ai_alerts":True,"biometric":False,"remember_device":True,"ai_suggestions":True,"automatic_explanations":True,"forecast_insights":True}

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

@st.cache_data
def load_transactions():
    if not TRANSACTIONS_FILE.exists():
        return pd.DataFrame(
            columns=["id", "date", "description", "category", "type", "amount"]
        )

    df = pd.read_csv(TRANSACTIONS_FILE)

    required = ["id", "date", "description", "category", "type", "amount"]
    for col in required:
        if col not in df.columns:
            if col == "id":
                df[col] = range(1, len(df) + 1)
            else:
                df[col] = ""

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
    output = df.copy()
    output["date"] = pd.to_datetime(output["date"]).dt.strftime("%Y-%m-%d")
    output.to_csv(TRANSACTIONS_FILE, index=False)
    load_transactions.clear()


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

def login_page():
    left, center, right = st.columns([1, 1.35, 1])

    with center:
        st.markdown(
            """
            <div class="hero">
                <span class="hero-badge">SMART FINANCE • MONEYFLOW</span>
                <h1>💼 MoneyFlow</h1>
                <p>Sign in to your financial command center.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Welcome back")

            mode = st.radio(
                "Login method",
                ["Email", "Phone"],
                horizontal=True,
                label_visibility="collapsed",
            )

            if mode == "Email":
                identifier = st.text_input("Email address", placeholder="you@example.com", key="login_email")
            else:
                identifier = st.text_input("Phone number", placeholder="+91 XXXXX XXXXX", key="login_phone")

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )

            if st.button("Sign in to MoneyFlow", use_container_width=True, type="primary"):
                identifier_clean = identifier.strip().lower() if identifier else ""
                password_clean = password if password else ""

                if not identifier_clean or not password_clean:
                    st.error("Please enter your login details.")
                else:
                    password_hash = hashlib.sha256(password_clean.encode("utf-8")).hexdigest()
                    stored_hash = st.session_state.demo_users.get(identifier_clean)

                    # First successful login for an identifier creates the demo credential.
                    if stored_hash is None:
                        st.session_state.demo_users[identifier_clean] = password_hash
                        st.session_state.logged_in = True
                        st.session_state.user_email = identifier_clean
                        st.session_state.user_name = (
                            identifier_clean.split("@")[0].replace(".", " ").title()
                            if "@" in identifier_clean
                            else "MoneyFlow User"
                        )
                        st.rerun()

                    # Existing identifier must use the same password.
                    elif hmac.compare_digest(stored_hash, password_hash):
                        st.session_state.logged_in = True
                        st.session_state.user_email = identifier_clean
                        st.session_state.user_name = (
                            identifier_clean.split("@")[0].replace(".", " ").title()
                            if "@" in identifier_clean
                            else "MoneyFlow User"
                        )
                        st.rerun()
                    else:
                        st.error("Credentials are not matching. Please check your password.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create account", use_container_width=True):
                    st.info("Account creation UI will be connected to the backend.")
            with col2:
                if st.button("Forgot password?", use_container_width=True):
                    st.info("Password recovery will be connected to secure authentication.")

        st.caption("Development authentication UI.")

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
            st.session_state.logged_in = False
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

def cfo_inside_dashboard(df):
    """AI CFO is intentionally embedded inside the dashboard, not a separate screen."""
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
                Your intelligent financial advisor is built directly into the dashboard.
                Ask a question and get a clear explanation from your financial data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_input(
        "Ask your AI CFO",
        placeholder="Example: Why are my expenses high? Which expense should I review?",
        key="dashboard_cfo_question",
    )

    quick1, quick2, quick3 = st.columns(3)

    quick_question = None
    if quick1.button("💸 Why are expenses high?", use_container_width=True, key="cfo_q1"):
        quick_question = "Why are my expenses high and what should I review?"
    if quick2.button("📌 Biggest expense?", use_container_width=True, key="cfo_q2"):
        quick_question = "What is my biggest expense and why does it matter?"
    if quick3.button("🛡️ Explain my risk", use_container_width=True, key="cfo_q3"):
        quick_question = "Explain my current financial risk in simple language."

    ask_clicked = st.button(
        "✨ Ask AI CFO",
        type="primary",
        use_container_width=True,
        key="ask_cfo_button",
    )
    final_question = quick_question or question

    if quick_question or ask_clicked:
        if not final_question or not final_question.strip():
            st.warning("Enter a question first.")
        else:
            context = f"""
You are the AI CFO inside MoneyFlow.

Use only this financial data:
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

Answer the user's question in simple language.
Explain the reasoning using the numbers.
Give practical financial guidance.
Do not invent transactions.

User question:
{final_question}
"""
            try:
                from src.ai_engine import ask_gemini

                with st.spinner("AI CFO is analysing your financial data..."):
                    response = ask_gemini(context)

                st.markdown(
                    f'<div class="insight-box">🧠 <b>CFO Analysis</b><br><br>{response}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as error:
                # Keep the app answerable even if Gemini is temporarily unavailable.
                q = final_question.lower()
                if "biggest" in q or "largest" in q:
                    fallback = (
                        f"Your largest expense category is {top_category} at {money(top_amount)}. "
                        f"Total expenses are {money(expenses)}, so this category is the first area to review "
                        f"when checking where most spending is concentrated."
                    )
                elif "risk" in q or "anomal" in q:
                    fallback = (
                        f"Your current transaction risk level is {overall}. "
                        f"MoneyFlow detected {counts['High']} high-risk, {counts['Medium']} medium-risk "
                        f"and {counts['Low']} low-risk expense transactions. "
                        f"Review any high- or medium-risk transactions first."
                    )
                elif "expense" in q or "spend" in q or "cost" in q:
                    fallback = (
                        f"Your total expenses are {money(expenses)}, equal to {ratio:.1f}% of income. "
                        f"The largest expense category is {top_category} at {money(top_amount)}. "
                        f"That category is the most useful place to begin reviewing costs."
                    )
                elif "profit" in q or "margin" in q:
                    fallback = (
                        f"Your current net profit is {money(profit)} from income of {money(income)} "
                        f"and expenses of {money(expenses)}. Your profit margin is {margin:.1f}%."
                    )
                elif "income" in q or "revenue" in q:
                    fallback = (
                        f"Your total income is {money(income)}. After {money(expenses)} in expenses, "
                        f"MoneyFlow calculates a net profit of {money(profit)}."
                    )
                else:
                    fallback = (
                        f"Based on the current MoneyFlow data: income is {money(income)}, expenses are "
                        f"{money(expenses)}, net profit is {money(profit)}, profit margin is {margin:.1f}%, "
                        f"expense ratio is {ratio:.1f}%, and overall transaction risk is {overall}."
                    )
                st.markdown(
                    f'<div class="insight-box">🧠 <b>CFO Analysis</b><br><br>{fallback}</div>',
                    unsafe_allow_html=True,
                )


def overview_page(df):
    page_header(
        "Good evening 👋",
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
        "Upload Excel, CSV, or structured PDF financial data and analyze it in MoneyFlow.",
    )

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">1. Upload Financial Dataset</div>',
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Choose a financial dataset",
            type=["xlsx", "xls", "csv", "pdf"],
            help=(
                "Required columns: date, description, category, type and amount. "
                "Excel/CSV is recommended; structured PDF tables are also supported."
            ),
            key="financial_dataset_uploader",
        )

        if uploaded:
            st.success(f"Uploaded: {uploaded.name}")
            suffix = Path(uploaded.name).suffix.lower()

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

    imported_df = st.session_state.get("imported_dataset")

    if imported_df is not None:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">2. Preview & Validate</div>',
                unsafe_allow_html=True,
            )

            st.dataframe(
                imported_df,
                use_container_width=True,
                height=300,
                hide_index=True,
            )

            normalized = imported_df.copy()
            normalized.columns = [
                str(column).strip().lower().replace(" ", "_")
                for column in normalized.columns
            ]

            # Common PDF/Excel naming variations.
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
                st.error(
                    "Missing required columns: "
                    + ", ".join(sorted(missing))
                    + ". Required: date, description, category, type, amount."
                )
            else:
                normalized["date"] = pd.to_datetime(
                    normalized["date"], errors="coerce"
                )
                normalized["amount"] = pd.to_numeric(
                    normalized["amount"].astype(str).str.replace(",", "", regex=False)
                    .str.replace("₹", "", regex=False)
                    .str.replace("Rs.", "", regex=False)
                    .str.strip(),
                    errors="coerce",
                )

                normalized["type"] = (
                    normalized["type"]
                    .astype(str)
                    .str.strip()
                    .str.title()
                )

                invalid_dates = int(normalized["date"].isna().sum())
                invalid_amounts = int(normalized["amount"].isna().sum())
                invalid_types = int(
                    (~normalized["type"].isin(["Income", "Expense"])).sum()
                )
                duplicates = int(normalized.duplicated().sum())

                a, b, c, d = st.columns(4)
                a.metric("Rows", len(normalized))
                b.metric(
                    "Invalid",
                    invalid_dates + invalid_amounts + invalid_types,
                )
                c.metric("Duplicates", duplicates)
                d.metric(
                    "Valid",
                    max(
                        0,
                        len(normalized)
                        - invalid_dates
                        - invalid_amounts
                        - invalid_types
                        - duplicates,
                    ),
                )

                if invalid_dates or invalid_amounts or invalid_types:
                    st.warning(
                        "Some rows contain invalid dates, amounts, or transaction types. "
                        "Only valid Income/Expense rows will be imported."
                    )

                if st.button(
                    "📥  Import Dataset into MoneyFlow",
                    type="primary",
                    use_container_width=True,
                    key="import_financial_dataset",
                ):
                    clean = normalized.dropna(
                        subset=[
                            "date",
                            "description",
                            "category",
                            "type",
                            "amount",
                        ]
                    ).copy()

                    clean = clean[
                        clean["type"].isin(["Income", "Expense"])
                    ].copy()

                    clean["amount"] = clean["amount"].abs()

                    # Remove exact duplicate records before import.
                    clean = clean.drop_duplicates(
                        subset=[
                            "date",
                            "description",
                            "category",
                            "type",
                            "amount",
                        ]
                    ).copy()

                    clean["id"] = range(1, len(clean) + 1)
                    clean = clean[
                        [
                            "id",
                            "date",
                            "description",
                            "category",
                            "type",
                            "amount",
                        ]
                    ]

                    save_transactions(clean)

                    st.session_state["imported_dataset"] = None
                    st.success(
                        f"Imported {len(clean)} validated transactions successfully."
                    )
                    st.rerun()

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">3. Current MoneyFlow Dataset</div>',
            unsafe_allow_html=True,
        )

        st.write(
            f"MoneyFlow currently contains **{len(load_transactions())} transactions** "
            f"from `{TRANSACTIONS_FILE.name}`."
        )

        st.dataframe(
            load_transactions().tail(10),
            use_container_width=True,
            hide_index=True,
        )


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
        "View the next-month financial forecast using the historical financial dataset.",
    )

    history = load_history()

    if history.empty:
        st.warning("Historical financial data was not found.")
        return

    with st.container(border=True):
        st.markdown('<div class="section-title">📚 Historical Financial Data</div>', unsafe_allow_html=True)
        st.dataframe(
            history.assign(
                month=history["month"].dt.strftime("%b %Y"),
                income=history["income"].map(money),
                expenses=history["expenses"].map(money),
                profit=history["profit"].map(money),
            ),
            use_container_width=True,
            hide_index=True,
        )

    # XGBoost forecast
    try:
        from xgboost import XGBRegressor

        data = history.copy()
        data["year"] = data["month"].dt.year
        data["month_number"] = data["month"].dt.month
        data["income_lag_1"] = data["income"].shift(1)
        data["expenses_lag_1"] = data["expenses"].shift(1)
        data["profit_lag_1"] = data["profit"].shift(1)

        train = data.dropna().copy()

        features = [
            "year",
            "month_number",
            "income_lag_1",
            "expenses_lag_1",
            "profit_lag_1",
        ]

        models = {}

        for target in ["income", "expenses", "profit"]:
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

        future = pd.DataFrame(
            [{
                "year": next_month.year,
                "month_number": next_month.month,
                "income_lag_1": latest["income"],
                "expenses_lag_1": latest["expenses"],
                "profit_lag_1": latest["profit"],
            }]
        )

        predicted_income = max(0, models["income"].predict(future)[0])
        predicted_expenses = max(0, models["expenses"].predict(future)[0])
        predicted_profit = predicted_income - predicted_expenses

        st.write("")
        p1, p2, p3 = st.columns(3)

        p1.metric(
            f"Predicted Income · {next_month.strftime('%b %Y')}",
            money(predicted_income),
        )
        p2.metric(
            "Predicted Expenses",
            money(predicted_expenses),
        )
        p3.metric(
            "Predicted Profit",
            money(predicted_profit),
        )

        with st.container(border=True):
            st.markdown('<div class="section-title">Forecast Interpretation</div>', unsafe_allow_html=True)
            forecast_margin = (predicted_profit / predicted_income * 100) if predicted_income else 0
            st.markdown(
                f'<div class="insight-box">📈 For {next_month.strftime("%B %Y")}, the model predicts '
                f'<b>{money(predicted_income)}</b> income, <b>{money(predicted_expenses)}</b> expenses and '
                f'<b>{money(predicted_profit)}</b> profit, implying a predicted profit margin of '
                f'<b>{forecast_margin:.1f}%</b>.</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Forecast is based on the available historical dataset and should be presented as a development/demo forecast, not a guaranteed financial prediction."
            )

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

    risk_df, counts, overall = risk_analysis(df)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Overall Risk", overall)
    r2.metric("🔴 High", counts["High"])
    r3.metric("🟠 Medium", counts["Medium"])
    r4.metric("🟢 Low", counts["Low"])

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)

        chart_df = pd.DataFrame(
            {
                "Risk": ["High", "Medium", "Low"],
                "Count": [
                    counts["High"],
                    counts["Medium"],
                    counts["Low"],
                ],
            }
        )

        fig = px.bar(
            chart_df,
            x="Risk",
            y="Count",
            text="Count",
        )

        fig.update_layout(
            height=300,
            font=dict(family="Times New Roman, Times, serif", color="#172033", size=13),
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(dtick=1, gridcolor="#e5e7eb"),
        )

        st.plotly_chart(fig, use_container_width=True, key="risk_distribution")

    with st.container(border=True):
        st.markdown('<div class="section-title">Flagged Transactions</div>', unsafe_allow_html=True)

        if risk_df.empty:
            st.info("No expense transactions available.")
        else:
            flagged = risk_df[risk_df["risk_level"] != "Low"].copy()

            if flagged.empty:
                st.success("No medium/high-risk transactions detected.")
            else:
                flagged["date"] = flagged["date"].dt.strftime("%Y-%m-%d")
                flagged["amount"] = flagged["amount"].map(money)

                st.dataframe(
                    flagged[
                        [
                            "date",
                            "description",
                            "category",
                            "amount",
                            "risk_level",
                        ]
                    ],
                    use_container_width=True,
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




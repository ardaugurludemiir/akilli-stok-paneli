import io
import numpy as np
import pandas as pd
import requests
import streamlit as st

# --- 1. PAGE CONFIGURATION & ACADEMIC BRANDING ---
st.set_page_config(
    page_title=(
        "SmartStock — Enterprise Supply Chain & Inventory Decision Support"
        " Platform"
    ),
    page_icon="📦",
    layout="wide",
)

# --- 2. CUSTOM INDUSTRIAL SAAS STYLES ---
st.markdown(
    """
    <style>
    .industrial-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 70px 40px;
        border-radius: 24px;
        color: white;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        line-height: 1.15;
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }
    .hero-desc {
        font-size: 1.15rem;
        color: #94a3b8;
        max-width: 750px;
        line-height: 1.6;
        margin-bottom: 0px;
    }
    .custom-section-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 12px;
    }
    .custom-section-desc {
        font-size: 1.05rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. CUSTOM INDUSTRIAL HERO SECTION (Etiket Kaldırıldı) ---
st.markdown(
    """
    <div class="industrial-hero">
        <div class="hero-title">Stochastic Intelligence.<br>Absolute Inventory Control.</div>
        <div class="hero-desc">
            An advanced decision support architecture built to eliminate stockout vulnerabilities, 
            optimize safety thresholds through statistical modeling, and bridge macroeconomic shifts with operational execution.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- 4. REAL-TIME EXCHANGE RATE INTEGRATION ---
def fetch_live_exchange_rate():
  try:
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=3)
    data = response.json()
    if "rates" in data and "TRY" in data["rates"]:
      return float(data["rates"]["TRY"])
  except:
    pass

  try:
    url_backup = "https://api.frankfurter.app/latest?from=USD&to=TRY"
    resp = requests.get(url_backup, timeout=3)
    d_backup = resp.json()
    return float(d_backup["rates"]["TRY"])
  except:
    return 34.50


# --- 5. SIDEBAR CONFIGURATION ---
st.sidebar.header("📁 Data & Parameters")
uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])
currency_choice = st.sidebar.radio(
    "Select Currency:", ["Turkish Lira (₺)", "US Dollar ($)"]
)

service_level_choice = st.sidebar.selectbox(
    "Target Service Level (Stockout Protection):",
    [
        "90% (Z = 1.28)",
        "95% (Z = 1.65 - Standard)",
        "99% (Z = 2.33)",
        "99.9% (Z = 3.09)",
    ],
    index=1,
)

if "90%" in service_level_choice:
  z_score = 1.28
elif "99.9%" in service_level_choice:
  z_score = 3.09
elif "99%" in service_level_choice:
  z_score = 2.33
else:
  z_score = 1.65

if st.sidebar.button("🔄 Refresh Rates & Dataset"):
  st.rerun()

default_csv_data = """Urun_Kodu,Satis_Miktari,Tedarik_Suresi,Mevcut_Stok,Birim_Maliyet,Depo_Lokasyonu
LAPTOP-X1,15,5,45,18500.0,Central Hub (Istanbul)
LAPTOP-X1,18,5,45,18500.0,Central Hub (Istanbul)
LAPTOP-X1,22,5,45,18500.0,Central Hub (Istanbul)
MONITOR-27,8,10,120,4200.0,Western Hub (Izmir)
MONITOR-27,2,10,120,4200.0,Western Hub (Izmir)
MONITOR-27,15,10,120,4200.0,Western Hub (Izmir)
MOUSE-WRL,45,3,30,350.0,Southern Hub (Adana)
MOUSE-WRL,50,3,30,350.0,Southern Hub (Adana)
SERVER-BLD,3,14,15,85000.0,Central Hub (Istanbul)
SERVER-BLD,4,14,15,85000.0,Central Hub (Istanbul)
KABLO-HDMI,10,2,500,75.0,Western Hub (Izmir)
KABLO-HDMI,12,2,500,75.0,Western Hub (Izmir)
KLAVYE-RGB,14,7,65,1250.0,Southern Hub (Adana)
KLAVYE-RGB,28,7,65,1250.0,Southern Hub (Adana)
"""

if uploaded_file is not None:
  df = pd.read_csv(uploaded_file, encoding="utf-8-sig", on_bad_lines="skip")
else:
  try:
    df = pd.read_csv("test_2.csv", encoding="utf-8-sig", on_bad_lines="skip")
  except:
    df = pd.read_csv(io.StringIO(default_csv_data))

df.columns = df.columns.str.strip()
item_list = df["Urun_Kodu"].unique()


# --- 6. NAVIGATION TABS (ZIGZAG / Z-PATTERN UNIQUE LAYOUTS) ---
tab_analysis, tab_abc, tab_risk, tab_warehouse, tab_budget, tab_scenario = (
    st.tabs([
        "🔍 Item-Level Analysis",
        "📊 ABC Inventory Classification",
        "🚨 Comprehensive Risk Matrix",
        "🏢 Multi-Echelon Warehouse",
        "💰 Working Capital Budget",
        "⚖️ Stochastic Scenario Simulation",
    ])
)

# ================= TAB 1: ITEM ANALYSIS (Solda Açıklama, Sağda İnteraktif Kart) =================
with tab_analysis:
  col_l1, col_r1 = st.columns([1.1, 0.9], gap="large")
  with col_l1:
    st.markdown(
        '<div class="custom-section-title">Granular SKU Evaluation & Decision'
        " Matrix</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Analyze individual stock keeping'
        " units using rigorous stochastic demand distributions and lead-time"
        " variances. Calculate exact safety stock requirements and automated"
        " reorder triggers.</div>",
        unsafe_allow_html=True,
    )
    selected_item = st.selectbox(
        "Select Item Code for Evaluation:", item_list, key="item_selector"
    )
  with col_r1:
    with st.container(border=True):
      st.markdown("### 📌 Live Status Preview")
      st.error(
          "🔴 **CRITICAL STOCKOUT

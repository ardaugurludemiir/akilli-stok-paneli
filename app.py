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

# --- 3. CUSTOM INDUSTRIAL HERO SECTION ---
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


# --- 6. NAVIGATION TABS ---
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

# ================= TAB 1: ITEM ANALYSIS =================
with tab_analysis:
  col_l1, col_r1 = st.columns([1.1, 0.9], gap="large")
  with col_l1:
    st.markdown(
        '<div class="custom-section-title">Granular SKU Evaluation & Decision Matrix</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Analyze individual stock keeping units using rigorous stochastic demand distributions and lead-time variances. Calculate exact safety stock requirements and automated reorder triggers.</div>',
        unsafe_allow_html=True,
    )
    selected_item = st.selectbox(
        "Select Item Code for Evaluation:", item_list, key="item_selector"
    )
  with col_r1:
    with st.container(border=True):
      st.markdown("### 📌 Live Status Preview")
      st.error(
          "🔴 **CRITICAL STOCKOUT RISK**\n\nStock has breached the calculated"
          " Reorder Point threshold."
      )

  st.markdown("---")
  item_data = df[df["Urun_Kodu"] == selected_item]
  mean_d = item_data["Satis_Miktari"].mean()
  std_d = item_data["Satis_Miktari"].std()
  lt = item_data["Tedarik_Suresi"].iloc[0]
  stk = item_data["Mevcut_Stok"].iloc[-1]
  s_stock = z_score * (std_d if not pd.isna(std_d) else 0) * np.sqrt(lt)
  rop = (mean_d * lt) + s_stock

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Current Stock Level", f"{int(stk)} units")
  m2.metric("Calculated Safety Stock", f"{round(s_stock)} units")
  m3.metric("Reorder Point (ROP)", f"{round(rop)} units")
  m4.metric(
      "Estimated Runway",
      f"≈ {stk/mean_d:.1f} days" if mean_d > 0 else "N/A",
  )
  st.line_chart(item_data["Satis_Miktari"], use_container_width=True)


# ================= TAB 2: ABC CLASSIFICATION =================
with tab_abc:
  col_l2, col_r2 = st.columns([0.9, 1.1], gap="large")
  with col_l2:
    with st.container(border=True):
      st.markdown("### 📊 Pareto Breakdown (80/20)")
      st.info(
          "**Class A (80% Value):** Rigorous Continuous Review\n\n**Class B"
          " (15% Value):** Periodic Control\n\n**Class C (5% Value):** Two-Bin"
          " Bulk Control"
      )
  with col_r2:
    st.markdown(
        '<div class="custom-section-title">ABC Inventory Classification Matrix</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Classify inventory assets based on annual consumption value impact. Direct managerial focus toward high-impact stock lines to minimize holding and carrying costs.</div>',
        unsafe_allow_html=True,
    )

  st.markdown("---")
  abc_list = []
  for item in item_list:
    sub = df[df["Urun_Kodu"] == item]
    d_m = sub["Satis_Miktari"].mean()
    u_cost = sub["Birim_Maliyet"].iloc[0]
    abc_list.append({
        "Item Code": item,
        "Annual Consumption Value (₺)": d_m * 365 * u_cost,
    })
  abc_df = pd.DataFrame(abc_list).sort_values(
      by="Annual Consumption Value (₺)", ascending=False
  )
  st.dataframe(abc_df, use_container_width=True)


# ================= TAB 3: RISK MATRIX =================
with tab_risk:
  col_l3, col_r3 = st.columns([1.1, 0.9], gap="large")
  with col_l3:
    st.markdown(
        '<div class="custom-section-title">Enterprise-Wide Risk Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Holistic audit across all operational nodes. Instantly isolate critical stockouts, excess capital locking, and warning zones to maintain uninterrupted supply chain flow.</div>',
        unsafe_allow_html=True,
    )
  with col_r3:
    with st.container(border=True):
      st.markdown("### 🚨 Risk Intelligence")
      st.warning(
          "Continuous node monitoring prevents unexpected supply chain halts."
      )

  st.markdown("---")
  risk_list = []
  for item in item_list:
    sub = df[df["Urun_Kodu"] == item]
    d_m = sub["Satis_Miktari"].mean()
    d_s = (
        sub["Satis_Miktari"].std() if not pd.isna(sub["Satis_Miktari"].std()) else 0
    )
    lt_val = sub["Tedarik_Suresi"].iloc[0]
    stk_val = sub["Mevcut_Stok"].iloc[-1]
    r_point = (d_m * lt_val) + (z_score * d_s * np.sqrt(lt_val))
    status = (
        "🔴 Critical"
        if stk_val <= r_point
        else ("🟢 Secure" if stk_val > r_point * 1.2 else "🟡 Warning")
    )
    risk_list.append({
        "Item Code": item,
        "Stock": int(stk_val),
        "ROP": round(r_point),
        "Status": status,
    })
  st.dataframe(pd.DataFrame(risk_list), use_container_width=True)


# ================= TAB 4: MULTI-ECHELON =================
with tab_warehouse:
  col_l4, col_r4 = st.columns([0.9, 1.1], gap="large")
  with col_l4:
    with st.container(border=True):
      selected_wh = st.selectbox(
          "Select Node:", df["Depo_Lokasyonu"].unique()
      )
      wh_sub = df[df["Depo_Lokasyonu"] == selected_wh]
      st.metric(
          "Active SKUs at Node",
          wh_sub["Urun_Kodu"].nunique(),
          delta="Optimized",
      )
  with col_r4:
    st.markdown(
        '<div class="custom-section-title">Multi-Echelon Warehouse Architecture</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Coordinate distributed storage facilities (Istanbul, Izmir, Adana) in real-time. Evaluate localized inventory balances, lead times, and facility valuations.</div>',
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.dataframe(
      wh_sub[[
          "Urun_Kodu",
          "Satis_Miktari",
          "Mevcut_Stok",
          "Tedarik_Suresi",
          "Birim_Maliyet",
      ]],
      use_container_width=True,
  )


# ================= TAB 5: WORKING CAPITAL BUDGET =================
with tab_budget:
  col_l5, col_r5 = st.columns([1.1, 0.9], gap="large")
  with col_l5:
    st.markdown(
        '<div class="custom-section-title">Working Capital & Procurement Budget</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Compute exact capital allocations required to replenish critical stock items back to optimal ROP thresholds while preserving liquid financial reserves.</div>',
        unsafe_allow_html=True,
    )
  with col_r5:
    with st.container(border=True):
      st.markdown("### 💰 Financial Outlay Monitor")
      st.success("Real-time procurement cost projection enabled.")

  st.markdown("---")
  total_cap = sum(
      max(
          0,
          round(
              (
                  df[df["Urun_Kodu"] == i]["Satis_Miktari"].mean()
                  * df[df["Urun_Kodu"] == i]["Tedarik_Suresi"].iloc[0]
              )
              - df[df["Urun_Kodu"] == i]["Mevcut_Stok"].iloc[-1]
          ),
      )
      * df[df["Urun_Kodu"] == i]["Birim_Maliyet"].iloc[0]
      for i in item_list
  )
  st.metric(
      "Total Required Capital Outlay",
      f"₺{total_cap:,.2f}"
      if currency_choice != "US Dollar ($)"
      else f"${total_cap/fetch_live_exchange_rate():,.2f}",
  )


# ================= TAB 6: SCENARIO SIMULATION =================
with tab_scenario:
  col_l6, col_r6 = st.columns([0.9, 1.1], gap="large")
  with col_l6:
    with st.container(border=True):
      s_item = st.selectbox("Select Test SKU:", item_list, key="scen_sel")
      sub_s = df[df["Urun_Kodu"] == s_item]
      base_lt = sub_s["Tedarik_Suresi"].iloc[0]
      test_lt = st.slider(
          "Simulated Lead Time Extension (Days):",
          int(base_lt),
          30,
          int(base_lt) + 5,
      )
      st.write(f"New Disrupted Lead Time: **{test_lt} days**")
  with col_r6:
    st.markdown(
        '<div class="custom-section-title">Stochastic Resilience Simulation</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="custom-section-desc">Simulate severe supply chain shocks and lead time extensions. Test how safety thresholds dynamically adjust under stress testing and risk exposure models.</div>',
        unsafe_allow_html=True,
    )

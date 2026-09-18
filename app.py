import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

# --- 1. PAGE CONFIGURATION & ACADEMIC BRANDING ---
st.set_page_config(
    page_title="SmartStock — Enterprise Supply Chain & Inventory Decision Support Platform",
    page_icon="📦",
    layout="wide"
)

st.title("📦 SmartStock Enterprise — Decision Support System")
st.markdown("*Advanced Inventory Optimization, Stochastic Demand Modeling, and Real-Time Currency Integration.*")
st.markdown("---")

# --- 2. REAL-TIME EXCHANGE RATE INTEGRATION ---
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
        return 34.50  # Fallback exchange rate

# --- 3. DATA MANAGEMENT & DATA QUALITY GUARD ---
st.sidebar.header("📁 Data Management")
st.sidebar.markdown("Upload historical inventory & demand logs.")
uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])

currency_choice = st.sidebar.radio("Select Currency:", ["Turkish Lira (₺)", "US Dollar ($)"])

if st.sidebar.button("🔄 Refresh Rates & Dataset"):
    st.rerun()

# Built-in robust academic test dataset
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
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig', on_bad_lines='skip')
        st.sidebar.success("Dataset successfully uploaded!")
    except Exception as e:
        st.error(f"Error parsing dataset: {e}")
        st.stop()
else:
    try:
        df = pd.read_csv("test_2.csv", encoding='utf-8-sig', on_bad_lines='skip')
        st.sidebar.info("📂 'test_2.csv' dataset loaded.")
    except:
        df = pd.read_csv(io.StringIO(default_csv_data))
        st.sidebar.info("💡 Standard benchmark dataset is active.")

df.columns = df.columns.str.strip()

# Data Quality Assurance (Anomaly Detection)
anomaly_logs = []

if "Urun_Kodu" not in df.columns:
    df["Urun_Kodu"] = "ITEM-001"
    anomaly_logs.append("⚠️ 'Urun_Kodu' missing. Default assigned.")

if "Satis_Miktari" not in df.columns:
    df["Satis_Miktari"] = 10.0
    anomaly_logs.append("⚠️ 'Satis_Miktari' missing. Default value 10 set.")

if "Tedarik_Suresi" not in df.columns:
    df["Tedarik_Suresi"] = 5
    anomaly_logs.append("⚠️ 'Tedarik_Suresi' missing. Default lead time set to 5 days.")

if "Mevcut_Stok" not in df.columns:
    df["Mevcut_Stok"] = 100
    anomaly_logs.append("⚠️ 'Mevcut_Stok' missing. Default inventory set to 100.")

if "Birim_Maliyet" not in df.columns:
    df["Birim_Maliyet"] = 50.0
    anomaly_logs.append("⚠️ 'Birim_Maliyet' missing. Default cost set to 50.0.")

if "Depo_Lokasyonu" not in df.columns:
    warehouses = ["Central Hub (Istanbul)", "Western Hub (Izmir)", "Southern Hub (Adana)"]
    df["Depo_Lokasyonu"] = np.random.choice(warehouses, size=len(df))
    anomaly_logs.append("ℹ️ 'Depo_Lokasyonu' simulated automatically.")

negative_sales = (df["Satis_Miktari"] < 0).sum()
if negative_sales > 0:
    df = df[df["Satis_Miktari"] >= 0]
    anomaly_logs.append(f"🛡️ Cleaned {negative_sales} anomalous negative demand records.")

if anomaly_logs:
    with st.sidebar.expander("🛡️ Data Quality & Audit Report"):
        for log in anomaly_logs:
            st.write(log)

st.markdown("---")

# --- 4. REAL-TIME MACROECONOMIC & PORTFOLIO VALUATION PANEL ---
@st.fragment(run_every=10)
def render_macro_panel(df_data, currency):
    live_rate = fetch_live_exchange_rate()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="💱 Real-Time USD/TRY Rate", value=f"₺{live_rate:.2f}", delta="Live Feed (10s)")
    
    total_tl_valuation = (df_data["Mevcut_Stok"] * df_data["Birim_Maliyet"]).sum()
    
    if currency == "US Dollar ($)":
        converted_val = total_tl_valuation / live_rate
        col2.metric(label="📦 Total Portfolio Valuation", value=f"${converted_val:,.2f}")
        col3.metric(label="📊 Active Denomination", value="USD ($)")
    else:
        col2.metric(label="📦 Total Portfolio Valuation", value=f"₺{total_tl_valuation:,.2f}")
        col3.metric(label="📊 Active Denomination", value="TRY (₺)")

render_macro_panel(df, currency_choice)
st.markdown("---")

# --- 5. ACADEMIC & ENTERPRISE NAVIGATION TABS ---
tab_analysis, tab_risk, tab_warehouse, tab_budget, tab_scenario = st.tabs([
    "🔍 Item-Level Analysis & Executive Synthesis", 
    "🚨 Comprehensive Risk Matrix", 
    "🏢 Multi-Echelon Warehouse Management", 
    "💰 Capital Budgeting & Working Capital", 
    "⚖️ Stochastic Scenario Simulation"
])

item_list = df["Urun_Kodu"].unique()

# ================= TAB 1: ITEM ANALYSIS & EXECUTIVE SYNTHESIS =================
with tab_analysis:
    st.header("🔍 Granular Item Analysis & Automated Executive Summary")
    selected_item = st.selectbox("Select Item Code for Stochastic Evaluation:", item_list, key="item_selector")

    item_data = df[df["Urun_Kodu"] == selected_item]

    mean_demand = item_data["Satis_Miktari"].mean()
    std_demand = item_data["Satis_Miktari"].std()
    lead_time = item_data["Tedarik_Suresi"].iloc[0]
    current_inventory = item_data["Mevcut_Stok"].iloc[-1]

    if pd.isna(std_demand):
        std_demand = 0.0

    # Stochastic Inventory Formulas (95% Service Level -> Z = 1.65)
    safety_stock = 1.65 * std_demand * np.sqrt(lead_time)
    reorder_point = (mean_demand * lead_time) + safety_stock
    estimated_depletion_days = current_inventory / mean_demand if mean_demand > 0 else 999

    if current_inventory <= reorder_point:
        status_icon = "🔴"
        status_text = "CRITICAL STOCKOUT RISK"
        status_msg = f"Inventory has fallen below the calculated Reorder Point (**{round(reorder_point)} units**). Immediate replenishment required."
        card_func = st.error
    elif current_inventory > (reorder_point * 2.5):
        status_icon = "🔵"
        status_text = "EXCESS INVENTORY / OVERSTOCK"
        status_msg = f"Stock level ({current_inventory} units) significantly exceeds operational thresholds. Capital immobilization detected."
        card_func = st.info
    elif current_inventory <= (reorder_point * 1.2):
        status_icon = "🟡"
        status_text = "WARNING / MONITOR CLOSELY"
        status_msg = f"Inventory level is approaching the reorder threshold. Enhanced monitoring advised."
        card_func = st.warning
    else:
        status_icon = "🟢"
        status_text = "OPTIMAL / SECURE"
        status_msg = "Inventory level is well above the reorder point. No immediate action required."
        card_func = st.success

    st.subheader(f"📌 Decision Matrix: {selected_item}")
    card_func(f"### {status_icon} {status_text}\n\n{status_msg}")

    st.markdown("### 🤖 Automated Executive Synthesis & Operational Insights")
    if current_inventory <= reorder_point:
        exec_summary = f"**{selected_item}** exhibits critical supply vulnerabilities. Given a mean daily demand of {mean_demand:.1f} units and a lead time of {lead_time} days, current stock will be completely depleted in {estimated_depletion_days:.1f} days. To maintain target service levels and prevent stockouts, an immediate replenishment order of **{round(reorder_point - current_inventory + safety_stock)} units** must be initiated."
    elif current_inventory > (reorder_point * 2.5):
        exec_summary = f"**{selected_item}** reflects excessive capital locking due to overstocking. Current holding costs are suboptimal. It is recommended to defer subsequent procurement cycles to optimize working capital."
    else:
        exec_summary = f"**{selected_item}** operates within a stable stochastic equilibrium. Demand variance is controlled, and supply chain continuity is maintained."
    st.info(exec_summary)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Current Stock Level", value=f"{int(current_inventory)} units")
    m2.metric(label="Calculated Safety Stock", value=f"{round(safety_stock)} units")
    m3.metric(label="Reorder Point (ROP)", value=f"{round(reorder_point)} units")
    m4.metric(label="Estimated Stock Runway", value=f"≈ {estimated_depletion_days:.1f} days")

    st.markdown("### 📈 Historical Demand Trend")
    st.line_chart(item_data["Satis_Miktari"], use_container_width=True)


# ================= TAB 2: COMPREHENSIVE RISK MATRIX =================
with tab_risk:
    st.header("🚨 Enterprise-Wide Risk Dashboard & Classification")
    
    risk_summary_list = []
    for item in item_list:
        sub_df = df[df["Urun_Kodu"] == item]
        d_mean = sub_df["Satis_Miktari"].mean()
        d_std = sub_df["Satis_Miktari"].std()
        if pd.isna(d_std): d_std = 0.0
        lt = sub_df["Tedarik_Suresi"].iloc[0]
        stk = sub_df["Mevcut_Stok"].iloc[-1]
        
        s_stock = 1.65 * d_std * np.sqrt(lt)
        rop = (d_mean * lt) + s_stock

        if stk <= rop:
            risk_status = "🔴 Critical"
        elif stk > (rop * 2.5):
            risk_status = "🔵 Excess Stock"
        elif stk <= (rop * 1.2):
            risk_status = "🟡 Warning"
        else:
            risk_status = "🟢 Secure"

        risk_summary_list.append({
            "Item Code": item,
            "Current Stock": int(stk),
            "Mean Daily Demand": round(d_mean, 1),
            "Reorder Point (ROP)": round(rop),
            "Status Classification": risk_status
        })

    st.dataframe(pd.DataFrame(risk_summary_list), use_container_width=True)


# ================= TAB 3: MULTI-ECHELON WAREHOUSE MANAGEMENT =================
with tab_warehouse:
    st.header("🏢 Multi-Echelon Warehouse Performance")
    st.markdown("Comparative analysis of inventory distribution across regional nodes.")

    selected_warehouse = st.selectbox("Select Warehouse Facility:", df["Depo_Lokasyonu"].unique())
    wh_data = df[df["Depo_Lokasyonu"] == selected_warehouse]

    wh_item_count = wh_data["Urun_Kodu"].nunique()
    wh_total_units = wh_data["Mevcut_Stok"].sum()
    wh_total_val_tl = (wh_data["Mevcut_Stok"] * wh_data["Birim_Maliyet"]).sum()
    
    current_exchange = canli_kur_getir()
    wh_valuation = wh_total_val_tl / current_exchange if currency_choice == "US Dollar ($)" else wh_total_val_tl
    symbol = "$" if currency_choice == "US Dollar ($)" else "₺"

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric(label="Unique Stock Keeping Units (SKUs)", value=wh_item_count)
    wc2.metric(label="Total Physical Stock", value=f"{int(wh_total_units)} units")
    wc3.metric(label="Warehouse Valuation", value=f"{symbol}{wh_valuation:,.2f}")

    st.dataframe(wh_data[["Urun_Kodu", "Satis_Miktari", "Mevcut_Stok", "Tedarik_Suresi", "Birim_Maliyet"]], use_container_width=True)


# ================= TAB 4: CAPITAL BUDGETING & WORKING CAPITAL =================
with tab_butce:
    st.header("💰 Working Capital Requirements & Procurement Budget")
    st.markdown("Total capital required to restore critical items to their optimal Reorder Points:")

    current_exchange = canli_kur_getir()
    total_capital_tl = 0
    budget_breakdown = []

    for item in item_list:
        sub_df = df[df["Urun_Kodu"] == item]
        d_mean = sub_df["Satis_Miktari"].mean()
        d_std = sub_df["Satis_Miktari"].std()
        if pd.isna(d_std): d_std = 0.0
        lt = sub_df["Tedarik_Suresi"].iloc[0]
        stk = sub_df["Mevcut_Stok"].iloc[-1]
        unit_cost_tl = sub_df["Birim_Maliyet"].iloc[0]

        s_stock = 1.65 * d_std * np.sqrt(lt)
        rop = (d_mean * lt) + s_stock

        deficit_qty = max(0, round(rop - stk))
        item_cost_tl = deficit_qty * unit_cost_tl
        total_capital_tl += item_cost_tl

        cost_display = unit_cost_tl / current_exchange if currency_choice == "US Dollar ($)" else unit_cost_tl
        total_display = item_cost_tl / current_exchange if currency_choice == "US Dollar ($)" else item_cost_tl
        cur_symbol = "$" if currency_choice == "US Dollar ($)" else "₺"

        if deficit_qty > 0:
            budget_breakdown.append({
                "Item Code": item,
                "Current Stock": int(stk),
                "Target ROP": round(rop),
                "Replenishment Quantity": deficit_qty,
                f"Unit Cost ({cur_symbol})": f"{cur_symbol}{cost_display:,.2f}",
                f"Total Capital Req. ({cur_symbol})": f"{cur_symbol}{total_display:,.2f}"
            })

    final_budget = total_capital_tl / current_exchange if currency_choice == "US Dollar ($)" else total_capital_tl
    final_symbol = "$" if currency_choice == "US Dollar ($)" else "₺"

    st.metric(label=f"Total Capital Outlay Required ({currency_choice})", value=f"{final_symbol}{final_budget:,.2f}")

    if budget_breakdown:
        st.subheader("📋 Procurement Capital Allocation Table")
        st.dataframe(pd.DataFrame(budget_breakdown), use_container_width=True)
    else:
        st.success("All operational SKUs maintain secure inventory levels. No immediate capital outlay required.")


# ================= TAB 5: STOCHASTIC SCENARIO SIMULATION =================
with tab_scenario:
    st.header("⚖️ Supply Chain Resilience & Lead Time Sensitivity Simulation")
    st.markdown("Evaluate the impact of supply chain disruptions (lead time extensions) on safety stock and reorder thresholds.")

    scen_item = st.selectbox("Select SKU for Scenario Testing:", item_list, key="scenario_selector")
    scen_data = df[df["Urun_Kodu"] == scen_item]
    s_mean = scen_data["Satis_Miktari"].mean()
    s_std = scen_data["Satis_Miktari"].std()
    if pd.isna(s_std): s_std = 0.0
    baseline_lt = scen_data["Tedarik_Suresi"].iloc[0]

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("📍 Scenario A (Baseline Performance)")
        lt_a = baseline_lt
        rop_a = (s_mean * lt_a) + (1.65 * s_std * np.sqrt(lt_a))
        st.write(f"* Lead Time: **{lt_a} days**")
        st.write(f"* Reorder Point (ROP): **{round(rop_a)} units**")

    with col_s2:
        st.subheader("⚠️ Scenario B (Disruption / Delay Model)")
        lt_b = st.slider("Disrupted Lead Time (Days):", int(baseline_lt), 30, int(baseline_lt) + 5)
        rop_b = (s_mean * lt_b) + (1.65 * s_std * np.sqrt(lt_b))
        st.write(f"* Lead Time: **{lt_b} days**")
        st.write(f"* Reorder Point (ROP): **{round(rop_b)} units**")
        
        delta_rop = round(rop_b - rop_a)
        st.warning(f"💡 If lead time increases by {lt_b - baseline_lt} days, the Reorder Point must be adjusted upward by **{delta_rop} units** to mitigate stockout risks.")

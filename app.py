import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import utils

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="SmartStock — Envanter Karar Destek Platformu",
    page_icon="📦",
    layout="wide",
)

st.title("📦 SmartStock Enterprise — Karar Destek Sistemi")
st.markdown(
    "*Envanter Optimizasyonu, Stokastik Talep Modelleme, EOQ, Talep Tahmini "
    "ve Gerçek Zamanlı Döviz Entegrasyonu.*"
)
st.markdown("---")

# --- 2. YAN PANEL: VERİ VE PARAMETRELER ---
st.sidebar.header("📁 Veri & Parametreler")
st.sidebar.markdown("Operasyonel parametreleri buradan yapılandırın.")

uploaded_file = st.sidebar.file_uploader("CSV Veri Seti Yükle", type=["csv"])
currency_choice = st.sidebar.radio("Para Birimi Seçin:", ["Turkish Lira (₺)", "US Dollar ($)"])

service_level_choice = st.sidebar.selectbox(
    "Hedef Hizmet Düzeyi (Stoksuz Kalma Koruması):",
    list(utils.Z_SCORE_OPTIONS.keys()),
    index=1,
)
z_score = utils.Z_SCORE_OPTIONS[service_level_choice]

if st.sidebar.button("🔄 Kurları & Veri Setini Yenile"):
    st.cache_data.clear()
    st.rerun()

# Dosya içeriğini cache-uyumlu şekilde byte olarak oku (Streamlit UploadedFile
# doğrudan hashlenemediği için cache_data fonksiyonuna byte geçiyoruz)
uploaded_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
uploaded_name = uploaded_file.name if uploaded_file is not None else None

try:
    df, anomaly_logs, data_source = utils.load_and_clean_data(uploaded_bytes, uploaded_name)
except ValueError as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

if uploaded_file is not None:
    st.sidebar.success("Veri seti başarıyla yüklendi!")
elif data_source.startswith("local_file"):
    st.sidebar.info("📂 'musteri_verisi.csv' veri seti yüklendi.")
else:
    st.sidebar.info("💡 Standart örnek (benchmark) veri seti aktif.")

if anomaly_logs:
    with st.sidebar.expander("🛡️ Veri Kalitesi & Denetim Raporu"):
        for log in anomaly_logs:
            st.write(log)

item_list = sorted(df["Urun_Kodu"].unique())
exchange_rate, rate_source = utils.fetch_live_exchange_rate()
symbol = utils.currency_symbol(currency_choice)

st.markdown("---")

# --- 3. ÜST KPI ÖZETİ ---
st.subheader("📌 Genel Durum Özeti")

risk_df_full = utils.build_risk_table(df, item_list, z_score)
n_critical = (risk_df_full["_status_code"] == "critical").sum()
n_warning = (risk_df_full["_status_code"] == "warning").sum()
n_excess = (risk_df_full["_status_code"] == "excess").sum()
n_optimal = (risk_df_full["_status_code"] == "optimal").sum()

total_tl_valuation = (df["Mevcut_Stok"] * df["Birim_Maliyet"]).sum()
total_valuation_display = utils.to_display_currency(total_tl_valuation, currency_choice, exchange_rate)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("💱 USD/TRY Kuru", f"₺{exchange_rate:.2f}", help=f"Kaynak: {rate_source}")
kpi2.metric("📦 Toplam Envanter Değeri", f"{symbol}{total_valuation_display:,.2f}")
kpi3.metric("🔴 Kritik SKU", int(n_critical))
kpi4.metric("🟡 Uyarı Seviyesinde SKU", int(n_warning))
kpi5.metric("🔵 Fazla Stoklu SKU", int(n_excess))

st.markdown("---")

# --- 4. SEKMELER ---
(
    tab_analysis,
    tab_forecast,
    tab_eoq,
    tab_abc,
    tab_risk,
    tab_warehouse,
    tab_budget,
    tab_scenario,
) = st.tabs(
    [
        "🔍 Ürün Analizi",
        "📈 Talep Tahmini",
        "📐 EOQ Hesaplayıcı",
        "📊 ABC Sınıflandırma",
        "🚨 Risk Matrisi",
        "🏢 Depo Yönetimi",
        "💰 Sermaye Bütçesi",
        "⚖️ Senaryo Simülasyonu",
    ]
)

# ================= TAB 1: ÜRÜN ANALİZİ =================
with tab_analysis:
    st.header("🔍 Detaylı Ürün Analizi & Otomatik Yönetici Özeti")

    selected_item = st.selectbox("Değerlendirilecek Ürün Kodu:", item_list, key="item_selector")
    item_data = df[df["Urun_Kodu"] == selected_item]
    stats = utils.compute_item_stats(item_data, z_score)

    status_code, icon, label = utils.classify_status(
        stats["current_inventory"], stats["reorder_point"]
    )
    status_func = {
        "critical": st.error,
        "excess": st.info,
        "warning": st.warning,
        "optimal": st.success,
    }[status_code]

    status_detail = {
        "critical": (
            f"Stok, hesaplanan sipariş noktasının altına düştü "
            f"(**{round(stats['reorder_point'])} birim**, Z={z_score}). Acil ikmal gerekiyor."
        ),
        "excess": "Stok seviyesi operasyonel eşiklerin belirgin şekilde üzerinde. Sermaye atıl kalıyor.",
        "warning": "Stok seviyesi sipariş noktasına yaklaşıyor. Yakın takip önerilir.",
        "optimal": "Stok seviyesi sipariş noktasının güvenli aralığında. Acil aksiyon gerekmiyor.",
    }[status_code]

    st.subheader(f"📌 Karar Matrisi: {selected_item} (Hizmet Düzeyi Z = {z_score})")
    status_func(f"### {icon} {label}\n\n{status_detail}")

    st.markdown("### 🤖 Otomatik Yönetici Özeti")
    if status_code == "critical":
        deficit = round(stats["reorder_point"] - stats["current_inventory"] + stats["safety_stock"])
        exec_summary = (
            f"**{selected_item}**, seçilen hizmet düzeyinde (Z={z_score}) kritik tedarik "
            f"riski gösteriyor. Ortalama günlük talep {stats['mean_demand']:.1f} birim, "
            f"tedarik süresi {stats['lead_time_mean']:.1f} gün olduğunda stok "
            f"{stats['estimated_depletion_days']:.1f} günde tükeniyor. "
            f"Önerilen acil sipariş miktarı: **{deficit} birim**."
        )
    elif status_code == "excess":
        exec_summary = (
            f"**{selected_item}** için fazla stoklanma nedeniyle sermaye kilitlenmesi söz konusu. "
            "Sonraki tedarik döngüleri ertelenmelidir."
        )
    else:
        exec_summary = f"**{selected_item}** stokastik dengede çalışıyor. Talep varyansı kontrol altında."
    st.info(exec_summary)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mevcut Stok", f"{int(stats['current_inventory'])} birim")
    m2.metric("Güvenlik Stoğu", f"{round(stats['safety_stock'])} birim")
    m3.metric("Sipariş Noktası (ROP)", f"{round(stats['reorder_point'])} birim")
    depletion_display = (
        "∞" if np.isinf(stats["estimated_depletion_days"])
        else f"≈ {stats['estimated_depletion_days']:.1f} gün"
    )
    m4.metric("Tahmini Stok Ömrü", depletion_display)

    st.markdown("### 📈 Geçmiş Talep Trendi")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=item_data["Satis_Miktari"].reset_index(drop=True),
            mode="lines+markers",
            name="Gerçekleşen Talep",
        )
    )
    fig.add_hline(
        y=stats["mean_demand"], line_dash="dot", line_color="gray",
        annotation_text="Ortalama Talep",
    )
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ================= TAB 2: TALEP TAHMİNİ =================
with tab_forecast:
    st.header("📈 Talep Tahmini (Basit Üstel Düzeltme)")
    st.markdown(
        "Geçmiş talep verisi üzerinden üstel düzeltme (exponential smoothing) ile "
        "kısa vadeli talep projeksiyonu üretir."
    )

    forecast_item = st.selectbox("Ürün Kodu:", item_list, key="forecast_selector")
    alpha = st.slider(
        "Düzeltme Katsayısı (α) — yüksek α yakın geçmişe daha çok ağırlık verir:",
        0.05, 0.9, 0.3, 0.05,
    )
    periods_ahead = st.slider("Kaç dönem ileri tahmin edilsin?", 1, 15, 5)

    f_data = df[df["Urun_Kodu"] == forecast_item]["Satis_Miktari"].reset_index(drop=True)
    smoothed, forecast = utils.exponential_smoothing_forecast(f_data, alpha, periods_ahead)

    if len(f_data) < 2:
        st.warning("Güvenilir bir tahmin için en az 2 geçmiş gözlem gerekiyor.")
    else:
        history_x = list(range(len(f_data)))
        forecast_x = list(range(len(f_data), len(f_data) + periods_ahead))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=history_x, y=f_data, mode="lines+markers", name="Gerçekleşen"))
        fig.add_trace(go.Scatter(x=history_x, y=smoothed, mode="lines", name="Düzeltilmiş (Smoothed)", line=dict(dash="dot")))
        fig.add_trace(go.Scatter(x=forecast_x, y=forecast, mode="lines+markers", name="Tahmin", line=dict(dash="dash", color="orange")))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Dönem", yaxis_title="Talep")
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            f"Önümüzdeki {periods_ahead} dönem için sabit tahmin: "
            f"**{forecast[-1]:.1f} birim/dönem**. "
            "Not: Basit üstel düzeltme trend ve mevsimselliği yakalamaz; "
            "güçlü trend gösteren ürünlerde Holt veya Holt-Winters yöntemleri tercih edilmelidir."
        )

# ================= TAB 3: EOQ HESAPLAYICI =================
with tab_eoq:
    st.header("📐 Ekonomik Sipariş Miktarı (EOQ) Hesaplayıcı")
    st.markdown(
        "Klasik EOQ formülü: **EOQ = √(2 × Yıllık Talep × Sipariş Maliyeti / Birim Elde Tutma Maliyeti)**"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        order_cost = st.number_input(
            f"Sipariş Başına Sabit Maliyet ({symbol}):", min_value=0.0, value=150.0, step=10.0
        )
    with col_b:
        holding_rate_pct = st.slider(
            "Yıllık Elde Tutma Maliyeti Oranı (birim maliyetin %'si):", 1, 50, 20
        )

    eoq_rows = []
    for item in item_list:
        sub = df[df["Urun_Kodu"] == item]
        d_mean = sub["Satis_Miktari"].mean()
        unit_cost_tl = sub["Birim_Maliyet"].iloc[0]
        annual_demand = d_mean * 365
        holding_cost_tl = unit_cost_tl * (holding_rate_pct / 100)

        order_cost_tl = order_cost if currency_choice != "US Dollar ($)" else order_cost * exchange_rate
        eoq_units = utils.compute_eoq(annual_demand, order_cost_tl, holding_cost_tl)
        orders_per_year = annual_demand / eoq_units if eoq_units > 0 else 0

        eoq_rows.append(
            {
                "Urun Kodu": item,
                "Yillik Talep (tahmini)": round(annual_demand),
                "Birim Elde Tutma Maliyeti (₺)": round(holding_cost_tl, 2),
                "Onerilen EOQ (birim)": round(eoq_units),
                "Yillik Siparis Sayisi": round(orders_per_year, 1),
            }
        )

    st.dataframe(pd.DataFrame(eoq_rows), use_container_width=True)
    st.caption(
        "EOQ, sipariş verme maliyeti ile stok bulundurma maliyeti arasındaki dengeyi optimize eder. "
        "Güvenlik stoğu hesabından bağımsızdır; ikisi birlikte kullanılmalıdır."
    )

# ================= TAB 4: ABC SINIFLANDIRMA =================
with tab_abc:
    st.header("📊 ABC Envanter Sınıflandırması (Pareto 80/20 Kuralı)")
    st.markdown(
        "SKU'lar, yıllık tüketim değerine göre sınıflandırılır ve yönetimsel odak buna göre önceliklendirilir."
    )

    abc_df = utils.build_abc_table(df, item_list)
    st.dataframe(abc_df, use_container_width=True)

    fig = go.Figure(
        go.Bar(x=abc_df["Urun Kodu"], y=abc_df["Yillik Tuketim Degeri (₺)"], name="Yıllık Değer")
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10), yaxis_title="₺")
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **A Sınıfı** ürünler toplam envanter değerinin ~%80'ini oluşturur ve sıkı, sürekli takip gerektirir.")

# ================= TAB 5: RİSK MATRİSİ =================
with tab_risk:
    st.header("🚨 Kurumsal Risk Panosu & Sınıflandırma")
    st.markdown("Satır renkleri stok durumunu gösterir: kırmızı=kritik, sarı=uyarı, mavi=fazla stok, yeşil=optimal.")
    styled_risk = utils.style_risk_table(risk_df_full)
    st.dataframe(styled_risk, use_container_width=True)

# ================= TAB 6: DEPO YÖNETİMİ =================
with tab_warehouse:
    st.header("🏢 Çok Katmanlı Depo Performansı")
    st.markdown("Bölgesel depolar arasında envanter dağılımının karşılaştırmalı analizi.")

    selected_warehouse = st.selectbox("Depo Seçin:", sorted(df["Depo_Lokasyonu"].unique()))
    wh_data = df[df["Depo_Lokasyonu"] == selected_warehouse]

    wh_item_count = wh_data["Urun_Kodu"].nunique()
    wh_total_units = wh_data["Mevcut_Stok"].sum()
    wh_total_val_tl = (wh_data["Mevcut_Stok"] * wh_data["Birim_Maliyet"]).sum()
    wh_valuation = utils.to_display_currency(wh_total_val_tl, currency_choice, exchange_rate)

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Benzersiz SKU Sayısı", wh_item_count)
    wc2.metric("Toplam Fiziksel Stok", f"{int(wh_total_units)} birim")
    wc3.metric("Depo Değerlemesi", f"{symbol}{wh_valuation:,.2f}")

    st.dataframe(
        wh_data[["Urun_Kodu", "Satis_Miktari", "Mevcut_Stok", "Tedarik_Suresi", "Birim_Maliyet"]],
        use_container_width=True,
    )

# ================= TAB 7: SERMAYE BÜTÇESİ =================
with tab_budget:
    st.header("💰 İşletme Sermayesi İhtiyacı & Tedarik Bütçesi")
    st.markdown("Kritik ürünleri optimal sipariş noktasına geri getirmek için gereken toplam sermaye:")

    total_capital_tl = 0.0
    budget_rows = []
    for item in item_list:
        sub = df[df["Urun_Kodu"] == item]
        stats_i = utils.compute_item_stats(sub, z_score)
        deficit_qty = max(0, round(stats_i["reorder_point"] - stats_i["current_inventory"]))
        item_cost_tl = deficit_qty * stats_i["unit_cost"]
        total_capital_tl += item_cost_tl

        if deficit_qty > 0:
            cost_display = utils.to_display_currency(stats_i["unit_cost"], currency_choice, exchange_rate)
            total_display = utils.to_display_currency(item_cost_tl, currency_choice, exchange_rate)
            budget_rows.append(
                {
                    "Urun Kodu": item,
                    "Mevcut Stok": int(stats_i["current_inventory"]),
                    "Hedef ROP": round(stats_i["reorder_point"]),
                    "Ikmal Miktari": deficit_qty,
                    f"Birim Maliyet ({symbol})": f"{symbol}{cost_display:,.2f}",
                    f"Toplam Sermaye ({symbol})": f"{symbol}{total_display:,.2f}",
                }
            )

    final_budget = utils.to_display_currency(total_capital_tl, currency_choice, exchange_rate)
    st.metric(f"Toplam Gerekli Sermaye ({currency_choice})", f"{symbol}{final_budget:,.2f}")

    if budget_rows:
        st.subheader("📋 Tedarik Sermaye Dağılım Tablosu")
        st.dataframe(pd.DataFrame(budget_rows), use_container_width=True)
    else:
        st.success("Tüm SKU'lar güvenli envanter seviyelerinde. Acil sermaye çıkışı gerekmiyor.")

# ================= TAB 8: SENARYO SİMÜLASYONU =================
with tab_scenario:
    st.header("⚖️ Tedarik Zinciri Dayanıklılığı & Tedarik Süresi Duyarlılık Simülasyonu")
    st.markdown("Tedarik zinciri aksaklıklarının (tedarik süresi uzaması) güvenlik stoğu ve sipariş noktasına etkisini değerlendirin.")

    scen_item = st.selectbox("Simülasyon için SKU Seçin:", item_list, key="scenario_selector")
    scen_data = df[df["Urun_Kodu"] == scen_item]
    s_mean = scen_data["Satis_Miktari"].mean()
    s_std = scen_data["Satis_Miktari"].std()
    s_std = 0.0 if pd.isna(s_std) else s_std
    baseline_lt = scen_data["Tedarik_Suresi"].mean()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("📍 Senaryo A (Temel Performans)")
        lt_a = baseline_lt
        rop_a = (s_mean * lt_a) + (z_score * s_std * np.sqrt(lt_a))
        st.write(f"* Tedarik Süresi: **{lt_a:.1f} gün**")
        st.write(f"* Sipariş Noktası (ROP): **{round(rop_a)} birim**")

    with col_s2:
        st.subheader("⚠️ Senaryo B (Aksama / Gecikme Modeli)")
        lt_b = st.slider("Aksamalı Tedarik Süresi (Gün):", int(baseline_lt), 30, int(baseline_lt) + 5)
        rop_b = (s_mean * lt_b) + (z_score * s_std * np.sqrt(lt_b))
        st.write(f"* Tedarik Süresi: **{lt_b} gün**")
        st.write(f"* Sipariş Noktası (ROP): **{round(rop_b)} birim**")

    delta_rop = round(rop_b - rop_a)
    st.warning(
        f"💡 Tedarik süresi {lt_b - baseline_lt:.1f} gün uzarsa, stoksuz kalma riskini azaltmak için "
        f"sipariş noktası **{delta_rop} birim** artırılmalıdır (Z={z_score})."
    )

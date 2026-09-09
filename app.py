import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Akıllı Stok Paneli", page_icon="📦")
st.title("📦 Akıllı Stok ve Karar Destek Sistemi")

# 1. DOSYA YÜKLEME ALANI (SaaS Özelliği)
st.sidebar.header("📁 Veri Yönetimi")
yuklenen_dosya = st.sidebar.file_uploader("Kendi CSV dosyanızı yükleyin", type=["csv"])

# 2. VERİYİ OKUMA (Yüklenen dosya varsa onu kullan, yoksa varsayılanı al)
if yuklenen_dosya is not None:
    df = pd.read_csv(yuklenen_dosya)
    st.sidebar.success("Dosya başarıyla yüklendi!")
else:
    df = pd.read_csv("musteri_verisi.csv")
    st.sidebar.info("Şu an örnek veri seti (musteri_verisi.csv) gösteriliyor.")

st.subheader("1. Müşteri Veritabanı")
st.dataframe(df)

# 3. ÜRÜN SEÇİMİ (AÇILIR MENÜ)
st.sidebar.subheader("2. Stok Optimizasyonu")
urun_listesi = df["Urun_Kodu"].unique()
secilen_urun = st.sidebar.selectbox("Analiz edilecek ürünü seçin:", urun_listesi)

# 4. HESAPLAMALAR VE KARAR DESTEK MODU
secilen_veri = df[df["Urun_Kodu"] == secilen_urun]

ortalama = secilen_veri["Satis_Miktari"].mean()
sapma = secilen_veri["Satis_Miktari"].std()
tedarik = secilen_veri["Tedarik_Suresi"].iloc[0]

if pd.isna(sapma):
    sapma = 0.0

# Sistem (Yapay Zeka) Önerilen Değerler
sistem_emniyet = 1.65 * sapma * np.sqrt(tedarik)
sistem_rop = (ortalama * tedarik) + sistem_emniyet

st.subheader("2. Stok Optimizasyonu ve Karar Destek")
st.markdown(f"**{secilen_urun}** kodlu ürün için analiz sonuçları:")

# Mod Seçimi (Manuel vs Yapay Zeka)
karar_modu = st.radio(
    "İnceleme Modunu Seçin:",
    ["🤖 Yapay Zeka / Sistem Önerisi", "🎛️ Manuel İnceleme (Simülasyon)"]
)

if karar_modu == "🤖 Yapay Zeka / Sistem Önerisi":
    aktif_emniyet = sistem_emniyet
    aktif_rop = sistem_rop
    st.info("💡 Sistem, veri setindeki dalgalanmaları (standart sapma) ve tedarik süresini baz alarak en güvenli optimizasyon değerlerini önerdi.")
else:
    st.warning("🎛️ Manuel moddasınız. Parametreleri kaydırarak kendi senaryolarınızı test edebilirsiniz.")
    manuel_hizmet_faktoru = st.slider("Hizmet Düzeyi Çarpanı (Z):", 1.0, 3.0, 1.65, 0.05)
    manuel_tedarik = st.slider("Tedarik Süresi (Gün):", 1, 30, int(tedarik))
    
    aktif_emniyet = manuel_hizmet_faktoru * sapma * np.sqrt(manuel_tedarik)
    aktif_rop = (ortalama * manuel_tedarik) + aktif_emniyet

# 5. SONUÇLARI GÖSTERME
col1, col2, col3 = st.columns(3)
col1.metric(label="Ortalama Satış", value=f"{ortalama:.1f} Adet")
col2.metric(label="Emniyet Stoku", value=f"{round(aktif_emniyet)} Adet")

delta_durumu = "Kritik Seviye" if aktif_rop > 100 else "Normal Seviye"
col3.metric(label="Sipariş Noktası", value=f"{round(aktif_rop)} Adet", delta=delta_durumu, delta_color="inverse")

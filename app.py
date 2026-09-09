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
    # Eğer dosya yüklenmediyse örnek veriyi okur
    df = pd.read_csv("musteri_verisi.csv")
    st.sidebar.info("Şu an örnek veri seti (musteri_verisi.csv) gösteriliyor.")

st.subheader("1. Müşteri Veritabanı")
st.dataframe(df)

# 3. ÜRÜN SEÇİMİ (AÇILIR MENÜ) - Sol Panele Taşındı
st.sidebar.subheader("2. Stok Optimizasyonu")

# Yüklenen verideki ürün kodlarını dinamik olarak çekiyoruz
urun_listesi = df["Urun_Kodu"].unique()
secilen_urun = st.sidebar.selectbox("Analiz edilecek ürünü seçin:", urun_listesi)

# 4. HESAPLAMALAR
secilen_veri = df[df["Urun_Kodu"] == secilen_urun]

ortalama = secilen_veri["Satis_Miktari"].mean()
sapma = secilen_veri["Satis_Miktari"].std()
tedarik = secilen_veri["Tedarik_Suresi"].iloc[0]

# Eğer standart sapma hesaplanamazsa (tek satırlık veri durumunda) hata almamak için önlem
if pd.isna(sapma):
    sapma = 0.0

emniyet_stoku = 1.65 * sapma * np.sqrt(tedarik)
yeni_rop = (ortalama * tedarik) + emniyet_stoku

# 5. SONUÇLARI GÖSTERME
st.subheader("2. Stok Optimizasyonu Sonuçları")
st.markdown(f"**{secilen_urun}** kodlu ürün için güncel metrikler:")

col1, col2, col3 = st.columns(3)
col1.metric(label="Ortalama Satış", value=f"{ortalama:.1f} Adet")
col2.metric(label="Emniyet Stoku", value=f"{round(emniyet_stoku)} Adet")
col3.metric(label="Sipariş Noktası", value=f"{round(yeni_rop)} Adet", delta="Kritik Seviye", delta_color="inverse")

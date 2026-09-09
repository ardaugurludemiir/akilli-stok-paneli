import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SAYFA YAPILANDIRMASI VE MARKALAŞMA ---
st.set_page_config(
    page_title="SmartStock — Akıllı Stok Analizi",
    page_icon="📦",
    layout="wide"
)

st.title("📦 SmartStock")
st.markdown("*Doğru ürünü, doğru zamanda, doğru miktarda stoklayın.*")
st.markdown("---")

# --- 2. DOSYA YÜKLEME ALANI (PROFESYONEL UX) ---
st.sidebar.header("📁 Veri Yönetimi")
st.sidebar.markdown("Stok verilerinizi CSV formatında yükleyin.")
yuklenen_dosya = st.sidebar.file_uploader("CSV Dosyası Yükle", type=["csv"])

# Veriyi okuma
if yuklenen_dosya is not None:
    df = pd.read_csv(yuklenen_dosya)
    st.sidebar.success("Dosya başarıyla yüklendi!")
else:
    try:
        df = pd.read_csv("musteri_verisi.csv")
        st.sidebar.info("Örnek veri seti (musteri_verisi.csv) gösteriliyor.")
    except:
        st.error("Lütfen geçerli bir CSV dosyası yükleyin.")
        st.stop()

# Gerekli sütun kontrolleri ve varsayılanlar
if "Mevcut_Stok" not in df.columns:
    df["Mevcut_Stok"] = 100  # Varsayılan stok kolonu yoksa ekle

# --- 3. GLOBAL KPI KARTLARI (TÜM DATASET İÇİN) ---
toplam_urun = df["Urun_Kodu"].nunique()
toplam_kayit = len(df)

# Stok değeri hesaplama (Eğer Birim_Maliyet varsa)
if "Birim_Maliyet" in df.columns:
    toplam_deger = (df["Mevcut_Stok"] * df["Birim_Maliyet"]).sum()
    deger_str = f"₺{toplam_deger:,.2f}"
else:
    deger_str = "Veri Yok"

st.subheader("📊 Genel Veri Özeti")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Toplam Ürün Çeşidi", value=toplam_urun)
kpi2.metric(label="Toplam Satış Kaydı", value=toplam_kayit)
kpi3.metric(label="Aktif Veri Aralığı", value="30 Günlük Simülasyon")
kpi4.metric(label="Toplam Stok Değeri", value=deger_str)

with st.expander("📄 Ham Veritabanını Görüntüle"):
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# --- 4. ÜRÜN SEÇİMİ VE ANALİZ BÖLÜMÜ ---
st.header("🔍 Akıllı Stok Analizi")
st.markdown("Satış hızınızı ve tedarik sürenizi analiz ederek optimum stok seviyesini belirleyin.")

urun_listesi = df["Urun_Kodu"].unique()
secilen_urun = st.selectbox("Analiz edilecek ürünü seçin:", urun_listesi)

# Seçilen ürünün verileri
secilen_veri = df[df["Urun_Kodu"] == secilen_urun]

ortalama_satis = secilen_veri["Satis_Miktari"].mean()
standart_sapma = secilen_veri["Satis_Miktari"].std()
tedarik_suresi = secilen_veri["Tedarik_Suresi"].iloc[0]
mevcut_stok = secilen_veri["Mevcut_Stok"].iloc[-1]

if pd.isna(standart_sapma):
    standart_sapma = 0.0

# --- 5. ANALİZ MODU (OTOMATİK vs SENARYO) ---
st.markdown("### ⚙️ Analiz Modu")
analiz_modu = st.radio(
    "Çalışma Modu Seçin:",
    ["🔘 Otomatik Analiz (Yapay Zeka Önerisi)", "⚪ Senaryo / Simülasyon (Manuel)"],
    horizontal=True
)

if analiz_modu.startswith("🔘"):
    aktif_tedarik = tedarik_suresi
    hizmet_faktoru = 1.65  # %95 Güven Düzeyi
    st.info("💡 Sistem, satış dalgalanması (standart sapma) ve tedarik süresini analiz ederek optimum seviyeleri belirledi.")
else:
    st.warning("🎛️ Simülasyon modundasınız. Farklı tedarik süreleri ve hizmet düzeylerini test edebilirsiniz.")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        hizmet_faktoru = st.slider("Güvenlik Çarpanı (Z):", 1.0, 3.0, 1.65, 0.05)
    with col_s2:
        aktif_tedarik = st.slider("Tedarik Süresi (Gün):", 1, 30, int(tedarik_suresi))

# Matematiksel Hesaplamalar
emniyet_stoku = hizmet_faktoru * standart_sapma * np.sqrt(aktif_tedarik)
siparis_noktasi = (ortalama_satis * aktif_tedarik) + emniyet_stoku
tahmini_gun = mevcut_stok / ortalama_satis if ortalama_satis > 0 else 999

# --- 6. DURUM TESPİTİ VE RENK SİSTEMİ ---
# Standart Etiketler: 🟢 GÜVENLİ | 🟡 DİKKAT | 🔴 KRİTİK | 🔵 FAZLA STOK
if mevcut_stok <= siparis_noktasi:
    durum_ikon = "🔴"
    durum_metin = "KRİTİK SEVİYE"
    durum_mesaj = f"**{round(siparis_noktasi)} adet** seviyesindeki sipariş noktasının altındasınız. Acil sipariş oluşturmanız öneriliyor."
    kart_fonk = st.error
elif mevcut_stok > (siparis_noktasi * 2.5):
    durum_ikon = "🔵"
    durum_metin = "FAZLA STOK"
    durum_mesaj = f"Mevcut stok ({mevcut_stok} adet) normal ihtiyacın oldukça üzerinde. Sermaye optimizasyonu önerilir."
    kart_fonk = st.info
elif mevcut_stok <= (siparis_noktasi * 1.2):
    durum_ikon = "🟡"
    durum_metin = "DİKKAT / İZLENMELİ"
    durum_mesaj = f"Stok seviyesi sipariş noktasına yaklaşıyor. Yakın takibe alınmalı."
    kart_fonk = st.warning
else:
    durum_ikon = "🟢"
    durum_metin = "GÜVENLİ"
    durum_mesaj = "Mevcut stok, önerilen sipariş noktasının üzerinde. Acil işlem gerekmiyor."
    kart_fonk = st.success

# --- 7. SONUÇ EKRANI VE BÜYÜK DURUM KARTI ---
st.markdown("---")
st.subheader(f"📌 {secilen_urun} — Stok Durumu")

# Büyük Durum Kartı
kart_fonk(f"### {durum_ikon} {durum_metin}\n\n{durum_mesaj}")

# Detaylı Metrik Kartları
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Mevcut Stok", value=f"{int(mevcut_stok)} adet")
m2.metric(label="Önerilen Emniyet Stoğu", value=f"{round(emniyet_stoku)} adet")
m3.metric(label="Sipariş Noktası (ROP)", value=f"{round(siparis_noktasi)} adet")
m4.metric(label="Tahmini Stok Ömrü", value=f"≈ {tahmini_gun:.1f} gün")

# --- 8. ŞEFFAFLIK ALANI: "NASIL HESAPLANDI?" ---
with st.expander("ℹ️ Nasıl hesaplandı? (Detaylı Matematiksel Döküm)"):
    st.markdown(f"""
    Bu karar, aşağıdaki operasyonel metrikler baz alınarak otomatik olarak hesaplanmıştır:
    * **Ortalama Günlük Satış:** `{ortalama_satis:.2f} adet/gün`
    * **Satış Dalgalanması (Std. Sapma):** `±{standart_sapma:.2f}`
    * **Tedarik Süresi:** `{aktif_tedarik} gün`
    * **Güvenlik / Hizmet Seviyesi (Z):** `%{95 if hizmet_faktoru == 1.65 else int(hizmet_faktoru*50)} (Z={hizmet_faktoru})`
    * **Emniyet Stoğu Tanımı:** Beklenmeyen satış artışları veya tedarik gecikmelerine karşı korunması gereken minimum yastık stok.
    * **Formül:** $\\text{Emniyet Stoğu} = Z \\times \\sigma \\times \\sqrt{L}$
    """)

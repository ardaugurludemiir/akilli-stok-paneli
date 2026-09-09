import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- 1. SAYFA YAPILANDIRMASI VE MARKALAŞMA ---
st.set_page_config(
    page_title="SmartStock — Akıllı Stok ve Tedarik Optimizasyonu",
    page_icon="📦",
    layout="wide"
)

st.title("📦 SmartStock Enterprise")
st.markdown("*Doğru ürünü, doğru zamanda, doğru miktarda stoklayın. Gelişmiş Karar Destek ve Optimizasyon Platformu.*")
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
    df["Mevcut_Stok"] = 100  
if "Birim_Maliyet" not in df.columns:
    df["Birim_Maliyet"] = 50.0  # Varsayılan maliyet

# --- 3. GLOBAL KPI KARTLARI & TOPLU RİSK PANORAMASI ---
toplam_urun = df["Urun_Kodu"].nunique()
toplam_kayit = len(df)
toplam_deger = (df["Mevcut_Stok"] * df["Birim_Maliyet"]).sum()

st.subheader("📊 Genel Veri ve Portföy Özeti")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Toplam Ürün Çeşidi", value=toplam_urun)
kpi2.metric(label="Toplam Satış Kaydı", value=toplam_kayit)
kpi3.metric(label="Aktif Veri Aralığı", value="30 Günlük Simülasyon")
kpi4.metric(label="Toplam Portföy Değeri", value=f"₺{toplam_deger:,.2f}")

with st.expander("📄 Ham Veritabanını Görüntüle"):
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# --- 4. SEKMELİ (TABS) KURUMSAL NAVİGASYON ---
tab_analiz, tab_toplu, tab_abc = st.tabs([
    "🔍 Ürün Bazlı Otomatik & Senaryo Analizi", 
    "🚨 Toplu Risk Panosu (Tüm Ürünler)", 
    "📈 ABC / XYZ Sınıflandırması"
])

# Ürün listesi
urun_listesi = df["Urun_Kodu"].unique()

# ================= TAB 1: ÜRÜN BAZLI ANALİZ & GRAFİK & EOQ & EXPORT =================
with tab_analiz:
    st.header("🔍 Detaylı Ürün Analizi ve Simülasyon")
    secilen_urun = st.selectbox("Analiz edilecek ürünü seçin:", urun_listesi, key="urun_secim_box")

    secilen_veri = df[df["Urun_Kodu"] == secilen_urun]

    ortalama_satis = secilen_veri["Satis_Miktari"].mean()
    standart_sapma = secilen_veri["Satis_Miktari"].std()
    tedarik_suresi = secilen_veri["Tedarik_Suresi"].iloc[0]
    mevcut_stok = secilen_veri["Mevcut_Stok"].iloc[-1]
    birim_maliyet = secilen_veri["Birim_Maliyet"].iloc[0]

    if pd.isna(standart_sapma):
        standart_sapma = 0.0

    # Çalışma Modu
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

    # Ekonomik Sipariş Miktarı (EOQ) Hesaplama (Varsayım: Yıllık talep = Ortalama*365, Sipariş Maliyeti = 500 TL, Elde Tutma Maliyeti = Birim * %20)
    yillik_talep = ortalama_satis * 365
    siparis_maliyeti = 500.0
    elde_tutma_maliyeti = birim_maliyet * 0.20
    if elde_tutma_maliyeti > 0 and yillik_talep > 0:
        eoq = np.sqrt((2 * yillik_talep * siparis_maliyeti) / elde_tutma_maliyeti)
    else:
        eoq = 100.0

    # Durum Tespiti
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

    st.markdown("---")
    st.subheader(f"📌 {secilen_urun} — Karar Paneli")
    kart_fonk(f"### {durum_ikon} {durum_metin}\n\n{durum_mesaj}")

    # Metrik Kartları
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(label="Mevcut Stok", value=f"{int(mevcut_stok)} adet")
    m2.metric(label="Emniyet Stoğu", value=f"{round(emniyet_stoku)} adet")
    m3.metric(label="Sipariş Noktası (ROP)", value=f"{round(siparis_noktasi)} adet")
    m4.metric(label="İdeal Sipariş (EOQ)", value=f"{round(eoq)} adet")
    m5.metric(label="Tahmini Stok Ömrü", value=f"≈ {tahmini_gun:.1f} gün")

    # Görsel Zaman Serisi Grafiği
    st.markdown("### 📈 Zaman İçindeki Satış Trendi")
    st.line_chart(secilen_veri["Satis_Miktari"], use_container_width=True)

    # Şeffaflık Alanı
    with st.expander("ℹ️ Nasıl hesaplandı? (Detaylı Matematiksel Döküm)"):
        st.markdown(r"""
        Bu karar, aşağıdaki operasyonel metrikler baz alınarak otomatik olarak hesaplanmıştır:
        * **Ortalama Günlük Satış:** `""" + f"{ortalama_satis:.2f}" + r""" adet/gün`
        * **Satış Dalgalanması (Std. Sapma):** `±""" + f"{standart_sapma:.2f}" + r"""`
        * **Tedarik Süresi:** `""" + str(aktif_tedarik) + r""" gün`
        * **Güvenlik / Hizmet Seviyesi (Z):** `Z=""" + str(hizmet_faktoru) + r"""`
        * **EOQ (Ekonomik Sipariş Miktarı):** Sabit sipariş ve elde tutma maliyetleri gözetilerek optimize edilen miktar.
        * **Formül:** $\text{Emniyet Stoğu} = Z \times \sigma \times \sqrt{L}$
        """)

    # CSV Rapor İndirme Butonu
    rapor_df = pd.DataFrame({
        "Urun_Kodu": [secilen_urun],
        "Mevcut_Stok": [mevcut_stok],
        "Ortalama_Satis": [ortalama_satis],
        "Emniyet_Stoku": [round(emniyet_stoku)],
        "Siparis_Noktasi": [round(siparis_noktasi)],
        "Ekonomik_Siparis_Miktari_EOQ": [round(eoq)],
        "Durum": [durum_metin]
    })
    csv_veri = rapor_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Bu Ürünün Analiz Raporunu İndir (CSV)",
        data=csv_veri,
        file_name=f"{secilen_urun}_akilli_stok_raporu.csv",
        mime='text/csv',
    )


# ================= TAB 2: TOPLU RİSK PANOSU =================
with tab_toplu:
    st.header("🚨 Tüm Ürünler İçin Toplu Risk Panoraması")
    st.markdown("Deponuzdaki tüm ürünlerin anlık sağlık durumunu tek ekranda inceleyin.")

    toplu_liste = []
    for u in urun_listesi:
        u_veri = df[df["Urun_Kodu"] == u]
        u_ort = u_veri["Satis_Miktari"].mean()
        u_sapma = u_veri["Satis_Miktari"].std()
        if pd.isna(u_sapma): u_sapma = 0.0
        u_tedarik = u_veri["Tedarik_Suresi"].iloc[0]
        u_stok = u_veri["Mevcut_Stok"].iloc[-1]
        
        u_emniyet = 1.65 * u_sapma * np.sqrt(u_tedarik)
        u_rop = (u_ort * u_tedarik) + u_emniyet

        if u_stok <= u_rop:
            durum = "🔴 Kritik"
        elif u_stok > (u_rop * 2.5):
            durum = "🔵 Fazla Stok"
        elif u_stok <= (u_rop * 1.2):
            durum = "🟡 Dikkat"
        else:
            durum = "🟢 Güvenli"

        toplu_liste.append({
            "Ürün Kodu": u,
            "Mevcut Stok": int(u_stok),
            "Günlük Ortalama Satış": round(u_ort, 1),
            "Sipariş Noktası": round(u_rop),
            "Emniyet Stoğu": round(u_emniyet),
            "Durum": durum
        })

    toplu_df = pd.DataFrame(toplu_liste)
    st.dataframe(toplu_df, use_container_width=True)


# ================= TAB 3: ABC / XYZ SINIFLANDIRMASI =================
with tab_abc:
    st.header("📈 ABC / XYZ Envanter Matrisi Sınıflandırması")
    st.markdown("Lojistik ve Tedarik Zinciri Yönetimi standartlarına göre ürünlerinizin stratejik sınıf analizi:")

    abc_liste = []
    for u in urun_listesi:
        u_veri = df[df["Urun_Kodu"] == u]
        u_ort = u_veri["Satis_Miktari"].mean()
        u_maliyet = u_veri["Birim_Maliyet"].iloc[0] if "Birim_Maliyet" in u_veri.columns else 50
        toplam_maliyet_degeri = u_ort * u_maliyet

        # Basit ABC Kuralı (Değere göre)
        if toplam_maliyet_degeri > 1000:
            abc_sinif = "A Sınıfı (Yüksek Değer)"
        elif toplam_maliyet_degeri > 300:
            abc_sinif = "B Sınıfı (Orta Değer)"
        else:
            abc_sinif = "C Sınıfı (Düşük Değer)"

        # Basit XYZ Kuralı (Talep dalgalanmasına göre)
        u_sapma = u_veri["Satis_Miktari"].std()
        if pd.isna(u_sapma) or u_sapma < 5:
            xyz_sinif = "X (Stabil Talep)"
        elif u_sapma < 15:
            xyz_sinif = "Y (Orta Dalgalanma)"
        else:
            xyz_sinif = "Z (Düzensiz / Vuruntulu Talep)"

        abc_liste.append({
            "Ürün Kodu": u,
            "ABC Analizi (Değer)": abc_sinif,
            "XYZ Analizi (Talep Kararlılığı)": xyz_sinif,
            "Stratejik Öneri": "Yakın Takip & JIT" if "A" in abc_sinif or "Z" in xyz_sinif else "Standart Kontrol"
        })

    abc_df = pd.DataFrame(abc_liste)
    st.dataframe(abc_df, use_container_width=True)

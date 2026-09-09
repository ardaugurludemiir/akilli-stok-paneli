import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SAYFA YAPILANDIRMASI VE MARKALAŞMA ---
st.set_page_config(
    page_title="SmartStock — Kurumsal Tedarik & Envanter Platformu",
    page_icon="📦",
    layout="wide"
)

st.title("📦 SmartStock Enterprise")
st.markdown("*Doğru ürünü, doğru zamanda, doğru miktarda stoklayın. Gelişmiş Karar Destek ve Optimizasyon Platformu.*")
st.markdown("---")

# --- 2. DOSYA YÜKLEME ALANI & VERİ KALİTESİ (ANOMALİ KONTROLÜ) ---
st.sidebar.header("📁 Veri Yönetimi")
st.sidebar.markdown("Stok ve sevkiyat verilerinizi yükleyin.")
yuklenen_dosya = st.sidebar.file_uploader("CSV Dosyası Yükle", type=["csv"])

# Veriyi okuma ve temizleme (Anomali Kontrolü)
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

# Eksik veya Hatalı Veri Temizleme (Data Quality Guard)
anomali_mesajlari = []
if "Mevcut_Stok" not in df.columns:
    df["Mevcut_Stok"] = 100
    anomali_mesajlari.append("⚠️ 'Mevcut_Stok' sütunu bulunamadı, varsayılan olarak 100 atandı.")

if "Birim_Maliyet" not in df.columns:
    df["Birim_Maliyet"] = 50.0
    anomali_mesajlari.append("⚠️ 'Birim_Maliyet' sütunu bulunamadı, varsayılan olarak 50.0 TL atandı.")

if "Depo_Lokasyonu" not in df.columns:
    # Çoklu depo desteği için varsayılan lokasyonlar dağıtalım
    lokasyonlar = ["Merkez Depo (İstanbul)", "Batı Depo (İzmir)", "Güney Depo (Adana)"]
    df["Depo_Lokasyonu"] = np.random.choice(lokasyonlar, size=len(df))
    anomali_mesajlari.append("ℹ️ 'Depo_Lokasyonu' sütunu otomatik oluşturuldu ve simüle edildi.")

# Negatif satış veya tedarik sürelerini temizleme
negatif_satis = (df["Satis_Miktari"] < 0).sum()
if negatif_satis > 0:
    df = df[df["Satis_Miktari"] >= 0]
    anomali_mesajlari.append(f"🛡️ {negatif_satis} adet negatif satış kaydı tespit edildi ve veri setinden temizlendi.")

# Anomali raporunu yan menüde göster
if anomali_mesajlari:
    with st.sidebar.expander("🛡️ Veri Kalitesi Raporu"):
        for m in anomali_mesajlari:
            st.write(m)

st.markdown("---")

# --- 3. SEKMELİ (TABS) KURUMSAL NAVİGASYON ---
tab_analiz, tab_toplu, tab_lokasyon, tab_butce, tab_senaryo = st.tabs([
    "🔍 Ürün Analizi & Yönetici Özeti", 
    "🚨 Toplu Risk Panosu", 
    "🏢 Çoklu Depo Yönetimi", 
    "💰 Finansal Bütçe Planı", 
    "⚖️ Senaryo Kıyaslama"
])

urun_listesi = df["Urun_Kodu"].unique()

# ================= TAB 1: ÜRÜN ANALİZİ & YÖNETİCİ ÖZETİ =================
with tab_analiz:
    st.header("🔍 Detaylı Ürün Analizi ve Akıllı Yönetici Özeti")
    secilen_urun = st.selectbox("Analiz edilecek ürünü seçin:", urun_listesi, key="urun_secim_box")

    secilen_veri = df[df["Urun_Kodu"] == secilen_urun]

    ortalama_satis = secilen_veri["Satis_Miktari"].mean()
    standart_sapma = secilen_veri["Satis_Miktari"].std()
    tedarik_suresi = secilen_veri["Tedarik_Suresi"].iloc[0]
    mevcut_stok = secilen_veri["Mevcut_Stok"].iloc[-1]
    birim_maliyet = secilen_veri["Birim_Maliyet"].iloc[0]

    if pd.isna(standart_sapma):
        standart_sapma = 0.0

    # Matematiksel Hesaplamalar
    emniyet_stoku = 1.65 * standart_sapma * np.sqrt(tedarik_suresi)
    siparis_noktasi = (ortalama_satis * tedarik_suresi) + emniyet_stoku
    tahmini_gun = mevcut_stok / ortalama_satis if ortalama_satis > 0 else 999

    # Durum Tespiti
    if mevcut_stok <= siparis_noktasi:
        durum_ikon = "🔴"
        durum_metin = "KRİTİK SEVİYE"
        durum_mesaj = f"**{round(siparis_noktasi)} adet** seviyesindeki sipariş noktasının altındasınız. Acil sipariş oluşturulmalıdır."
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

    st.subheader(f"📌 {secilen_urun} — Karar Paneli")
    kart_fonk(f"### {durum_ikon} {durum_metin}\n\n{durum_mesaj}")

    # Otomatik Türkçe Yönetici Özeti (AI Executive Summary)
    st.markdown("### 🤖 Otomatik Yönetici Özeti & İçgörü")
    if mevcut_stok <= siparis_noktasi:
        yonetici_ozeti = f"**{secilen_urun}** kodlu ürün için acil müdahale gerekmektedir. Günlük ortalama {ortalama_satis:.1f} adetlik talep hızı ve {tedarik_suresi} günlük tedarik süresi göz önüne alındığında, mevcut stok {tahmini_gun:.1f} gün içinde tamamen tükecektir. Finansal risk oluşmaması adına derhal {round(siparis_noktasi - mevcut_stok + emniyet_stoku)} adetlik tedarik planı devreye alınmalıdır."
    elif mevcut_stok > (siparis_noktasi * 2.5):
        yonetici_ozeti = f"**{secilen_urun}** kodlu üründe aşırı sermaye bağlanması (aşırı stok) tespit edilmiştir. Mevcut stok seviyesi normal operasyonel ihtiyacın çok üzerindedir. Depolama maliyetlerini düşürmek için sonraki alımların ertelenmesi tavsiye edilir."
    else:
        yonetici_ozeti = f"**{secilen_urun}** kodlu ürün operasyonel olarak sağlıklı bir dengededir. Talep dalgalanmaları kontrol altındadır ve tedarik zinciri kesintisiz çalışmaktadır."
    st.info(yonetici_ozeti)

    # Metrik Kartları
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Mevcut Stok", value=f"{int(mevcut_stok)} adet")
    m2.metric(label="Emniyet Stoğu", value=f"{round(emniyet_stoku)} adet")
    m3.metric(label="Sipariş Noktası (ROP)", value=f"{round(siparis_noktasi)} adet")
    m4.metric(label="Tahmini Stok Ömrü", value=f"≈ {tahmini_gun:.1f} gün")

    # Çizgi Grafik
    st.markdown("### 📈 Satış Trendi")
    st.line_chart(secilen_veri["Satis_Miktari"], use_container_width=True)


# ================= TAB 2: TOPLU RİSK PANOSU =================
with tab_toplu:
    st.header("🚨 Tüm Ürünler İçin Toplu Risk Panoraması")
    
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
            "Günlük Ortalama": round(u_ort, 1),
            "Sipariş Noktası": round(u_rop),
            "Durum": durum
        })

    st.dataframe(pd.DataFrame(toplu_liste), use_container_width=True)


# ================= TAB 3: ÇOKLU DEPO YÖNETİMİ =================
with tab_lokasyon:
    st.header("🏢 Lokasyon Bazlı Depo Yönetimi")
    st.markdown("Farklı şehirlerdeki depolarınızın envanter performansını karşılaştırın.")

    secilen_depo = st.selectbox("Depo Lokasyonu Seçin:", df["Depo_Lokasyonu"].unique())
    depo_veri = df[df["Depo_Lokasyonu"] == secilen_depo]

    d_urun_sayisi = depo_veri["Urun_Kodu"].nunique()
    d_toplam_stok = depo_veri["Mevcut_Stok"].sum()
    d_toplam_deger = (depo_veri["Mevcut_Stok"] * depo_veri["Birim_Maliyet"]).sum()

    dc1, dc2, dc3 = st.columns(3)
    dc1.metric(label="Depodaki Ürün Çeşidi", value=d_urun_sayisi)
    dc2.metric(label="Toplam Stok Adedi", value=f"{int(d_toplam_stok)} adet")
    dc3.metric(label="Depo Envanter Değeri", value=f"₺{d_toplam_deger:,.2f}")

    st.dataframe(depo_veri[["Urun_Kodu", "Satis_Miktari", "Mevcut_Stok", "Tedarik_Suresi", "Birim_Maliyet"]], use_container_width=True)


# ================= TAB 4: FİNANSAL BÜTÇE PLANLAYICISI =================
with tab_butce:
    st.header("💰 Finansal Bütçe ve Sermaye Optimizasyonu")
    st.markdown("Kritik seviyedeki ürünleri güvenli seviyeye çıkarmak için gereken toplam bütçe ihtiyacı:")

    toplam_butce_ihtiyaci = 0
    butce_liste = []

    for u in urun_listesi:
        u_veri = df[df["Urun_Kodu"] == u]
        u_ort = u_veri["Satis_Miktari"].mean()
        u_sapma = u_veri["Satis_Miktari"].std()
        if pd.isna(u_sapma): u_sapma = 0.0
        u_tedarik = u_veri["Tedarik_Suresi"].iloc[0]
        u_stok = u_veri["Mevcut_Stok"].iloc[-1]
        u_maliyet = u_veri["Birim_Maliyet"].iloc[0]

        u_emniyet = 1.65 * u_sapma * np.sqrt(u_tedarik)
        u_rop = (u_ort * u_tedarik) + u_emniyet

        # Eğer mevcut stok ROP altındaysa aradaki fark kadar sipariş maliyeti ekle
        eksik_miktar = max(0, round(u_rop - u_stok))
        urun_butce_maliyeti = eksik_miktar * u_maliyet
        toplam_butce_ihtiyaci += urun_butce_maliyeti

        if eksik_miktar > 0:
            butce_liste.append({
                "Ürün Kodu": u,
                "Mevcut Stok": int(u_stok),
                "Hedeflenen Sipariş Noktası": round(u_rop),
                "Alınması Gereken Adet": eksik_miktar,
                "Birim Maliyet (TL)": f"₺{u_maliyet:,.2f}",
                "Toplam Maliyet (TL)": f"₺{urun_butce_maliyeti:,.2f}"
            })

    st.metric(label="Acil Tedarik İçin Toplam Nakit İhtiyacı", value=f"₺{toplam_butce_ihtiyaci:,.2f}")

    if butce_liste:
        st.subheader("📋 Tedarik Maliyet Dağılım Tablosu")
        st.dataframe(pd.DataFrame(butce_liste), use_container_width=True)
    else:
        st.success("Tebrikler! Hiçbir üründe acil bütçe gerektiren kritik açık bulunmuyor.")


# ================= TAB 5: YAN YANA SENARYO KIYASLAMA =================
with tab_senaryo:
    st.header("⚖️ Tedarik Süresi & Esneklik Senaryo Kıyaslaması")
    st.markdown("Tedarik zincirinde olası aksamaların (gecikmelerin) emniyet stoğuna ve sipariş noktasına etkisini yan yana test edin.")

    s_urun = st.selectbox("Senaryo İçin Ürün Seçin:", urun_listesi, key="senaryo_urun")
    s_veri = df[df["Urun_Kodu"] == s_urun]
    s_ort = s_veri["Satis_Miktari"].mean()
    s_sapma = s_veri["Satis_Miktari"].std()
    if pd.isna(s_sapma): s_sapma = 0.0
    orijinal_tedarik = s_veri["Tedarik_Suresi"].iloc[0]

    sc1, sc2 = st.columns(2)
    with sc1:
        st.subheader("📍 Senaryo A (Normal Şartlar)")
        tedarik_a = orijinal_tedarik
        rop_a = (s_ort * tedarik_a) + (1.65 * s_sapma * np.sqrt(tedarik_a))
        st.write(f"* Tedarik Süresi: **{tedarik_a} gün**")
        st.write(f"* Önerilen Sipariş Noktası: **{round(rop_a)} adet**")

    with sc2:
        st.subheader("⚠️ Senaryo B (Kriz / Gecikme Durumu)")
        tedarik_b = st.slider("Kriz Durumundaki Tedarik Süresi (Gün):", int(orijinal_tedarik), 30, int(orijinal_tedarik) + 5)
        rop_b = (s_ort * tedarik_b) + (1.65 * s_sapma * np.sqrt(tedarik_b))
        st.write(f"* Tedarik Süresi: **{tedarik_b} gün**")
        st.write(f"* Önerilen Sipariş Noktası: **{round(rop_b)} adet**")
        
        fark = round(rop_b - rop_a)
        st.warning(f"💡 Tedarik süresi {tedarik_b - orijinal_tedarik} gün uzarsa, sipariş noktasını **{fark} adet** yukarı çekmeniz gerekir!")

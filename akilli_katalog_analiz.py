
import streamlit as st
import pandas as pd
from modules import yazim_kontrol, kategori_kontrol, gorsel_kontrol, kalite_skori, kategori_onerisi

st.set_page_config(page_title="Akıllı Katalog Analiz Sistemi", layout="wide")
st.title("📦 Akıllı Katalog Analiz Sistemi")

uploaded_file = st.file_uploader("Katalog dosyasını yükleyin (.csv veya .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

    df["yazim_sorunu"] = df["title"].apply(yazim_kontrol.tespit_et)
    df["tahmin_edilen_kategori"] = df["title"].apply(kategori_onerisi.tahmin_et)
    df["kategori_uyusmazligi"] = df.apply(kategori_kontrol.karsilastir, axis=1)
    df["gorsel_durumu"] = df["image_url"].apply(gorsel_kontrol.kontrol_et)
    df["kalite_skoru"] = df.apply(kalite_skori.hesapla, axis=1)

    st.success("✅ Dosya başarıyla yüklendi.")
    st.subheader("📊 Analiz Sonuçları")
    st.dataframe(df)

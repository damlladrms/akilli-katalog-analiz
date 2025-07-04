
import streamlit as st
import pandas as pd
import difflib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sayfa başlığı
st.set_page_config(page_title="Akıllı Katalog Analiz Sistemi", layout="wide")
st.title("📦 Akıllı Katalog Analiz Sistemi")

st.markdown("Katalog dosyasını yükleyin (.csv veya .xlsx)")

uploaded_file = st.file_uploader("Dosya yükleyerek başlayın.", type=["csv", "xlsx"])

def load_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df

def check_spelling(title):
    kelimeler = title.split()
    suggestions = []
    for kelime in kelimeler:
        if len(kelime) > 15 or any(c.isdigit() for c in kelime):
            suggestions.append(kelime)
    return len(suggestions) > 0

def kategori_uyusmazligi(mevcut, tahmin):
    return mevcut.strip().lower() != tahmin.strip().lower()

def kategori_tahmin_et(baslik):
    if any(x in baslik.lower() for x in ["mont", "ceket", "elbise", "pantolon"]):
        return "Giyim"
    elif any(x in baslik.lower() for x in ["ayakkabı", "bot"]):
        return "Ayakkabı"
    elif any(x in baslik.lower() for x in ["kulaklık", "bluetooth", "telefon"]):
        return "Elektronik"
    else:
        return "Diğer"

if uploaded_file:
    df = load_data(uploaded_file)

    if not {"title", "category"}.issubset(df.columns):
        st.error("⛔ Gerekli sütunlar eksik. Lütfen 'title' ve 'category' başlıklarını içeren dosya yükleyin.")
    else:
        df["tahmin_edilen_kategori"] = df["title"].apply(kategori_tahmin_et)
        df["kategori_uyusmazligi"] = df.apply(lambda x: kategori_uyusmazligi(x["category"], x["tahmin_edilen_kategori"]), axis=1)
        df["yazim_sorunu"] = df["title"].apply(check_spelling)

        st.success("✅ Dosya başarıyla yüklendi.")
        st.subheader("📊 Analiz Sonuçları")

        st.dataframe(df[["title", "category", "tahmin_edilen_kategori", "kategori_uyusmazligi", "yazim_sorunu"]])

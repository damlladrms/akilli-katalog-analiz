
import streamlit as st
import pandas as pd
import difflib
from PIL import Image
import os

st.set_page_config(page_title="Akıllı Katalog Analiz", layout="wide")

st.title("🧠 Akıllı Katalog Analiz Sistemi")

uploaded_file = st.file_uploader("Lütfen katalog dosyasını (.xlsx) yükleyin", type=["xlsx"])

def spelling_check(word):
    dictionary = ["elbise", "mont", "kulaklık", "ayakkabı", "çanta", "pantolon"]
    matches = difflib.get_close_matches(word.lower(), dictionary, n=1, cutoff=0.8)
    return matches[0] if matches else None

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in ["title", "category", "subcategory"]):
        st.error("⛔ Gerekli sütunlar eksik. Lütfen 'title', 'category', 'subcategory' sütunlarını içeren dosya yükleyin.")
    else:
        st.success("✅ Dosya başarıyla yüklendi.")

        analiz_sonuclari = []
        for _, row in df.iterrows():
            title = str(row["title"])
            category = str(row["category"])
            subcategory = str(row["subcategory"])

            # Yazım kontrolü
            corrected_title = spelling_check(title.split()[0]) or title.split()[0]
            spelling_issue = corrected_title != title.split()[0]

            # Kategori önerisi
            keyword_map = {
                "kulaklık": "Elektronik",
                "mont": "Giyim",
                "elbise": "Giyim",
                "ayakkabı": "Giyim",
                "çanta": "Aksesuar",
                "pantolon": "Giyim"
            }

            predicted_cat = ""
            for keyword, cat in keyword_map.items():
                if keyword in title.lower():
                    predicted_cat = cat
                    break

            cat_match = predicted_cat == category

            analiz_sonuclari.append({
                "Ürün Başlığı": title,
                "Mevcut Kategori": category,
                "Tahmin Edilen Kategori": predicted_cat or "-",
                "Kategori Uyuşuyor mu?": "✅" if cat_match else "❌",
                "Yazım Sorunu": "⚠️" if spelling_issue else "✅"
            })

        st.markdown("### 📊 Analiz Sonuçları")
        st.dataframe(pd.DataFrame(analiz_sonuclari))

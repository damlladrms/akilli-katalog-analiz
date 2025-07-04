import streamlit as st
import pandas as pd
from kategori_oneri import kategori_tahmin_et
from yazim_kontrol import yazim_hatasi_var_mi
from kalite_skori import kalite_skoru_hesapla
from gorsel_kontrol import gorsel_kalite_kontrolu

st.set_page_config(page_title="Akıllı Katalog Analiz Sistemi", layout="wide")

st.title("📦 Akıllı Katalog Analiz Sistemi")

uploaded_file = st.file_uploader("Katalog dosyasını yükleyin (.csv veya .xlsx)", type=["csv", "xlsx"])
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if not set(["title", "category", "image_path"]).issubset(df.columns):
            st.error("⛔ Gerekli sütunlar eksik. Lütfen 'title', 'image_path', 'category' başlıklarını içeren dosya yükleyin.")
        else:
            df["tahmin_edilen_kategori"] = df["title"].apply(kategori_tahmin_et)
            df["kategori_uyusmazligi"] = df["category"] != df["tahmin_edilen_kategori"]
            df["yazim_sorunu"] = df["title"].apply(yazim_hatasi_var_mi)
            df["gorsel_durumu"] = df["image_path"].apply(gorsel_kalite_kontrolu)
            df["kalite_skoru"] = df.apply(kalite_skoru_hesapla, axis=1)

            st.success("✅ Dosya başarıyla analiz edildi.")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Sonuçları İndir (CSV)", data=csv, file_name="analiz_sonuclari.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")
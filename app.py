
import streamlit as st
import pandas as pd
from kategori_oneri import kategori_tahmin_et
from yazim_kontrol import yazim_var_mi
from kalite_skori import kalite_puani_hesapla

st.set_page_config(page_title="Akıllı Katalog Analiz", layout="wide")
st.title("📊 Akıllı Katalog Analiz")
st.markdown("Lütfen katalog dosyasını (.xlsx) yükleyin")

uploaded_file = st.file_uploader("Dosya Yükle", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Dosya başarıyla yüklendi.")
    st.subheader("🧾 Yüklenen Veri")
    st.dataframe(df)

    st.subheader("🤖 Otomatik Analiz")
    st.markdown("Aşağıda analiz sonuçları gösterilmektedir.")

    results = df.copy()
    results["Recommended Category"] = df["title"].apply(kategori_tahmin_et)
    results["yazim_sorunu"] = df["title"].apply(yazim_var_mi)
    results["kategori_uyusmazligi"] = df.apply(
        lambda row: row["category"] != kategori_tahmin_et(row["title"]), axis=1
    )
    results["Kalite Skoru"] = df.apply(kalite_puani_hesapla, axis=1)
    results["Analiz Sonucu"] = results.apply(
        lambda row: "❌ Başlık '{}' içeriyor ama ana kategori uyumsuz.".format(row["title"].split()[0])
        if row["kategori_uyusmazligi"]
        else ("⚠️ Yazım hatası var." if row["yazim_sorunu"] else "✅ Sorun yok."),
        axis=1,
    )

    st.subheader("📊 Analiz Sonuçları")
    st.dataframe(results)

    st.download_button("📥 Sonuçları İndir", results.to_csv(index=False), "analiz_sonuclari.csv", "text/csv")
    
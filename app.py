# app.py  —  AKILLI KATALOG ANALİZ (tam ve sade)

import streamlit as st
import pandas as pd

# ---- Yerel modüller (aynı klasörde) ----
from yazim_kontrol import quick_spelling_checks
from kategori_oneri import suggest_category
from kalite_skori import compute_quality_score
from gorsel_kontrol import check_image_text_match_placeholder


# ---------------- Yardımcılar ----------------
def read_table(uploaded_file):
    """CSV/XLSX dosyayı oku ve kolon adlarını normalize et"""
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        # ayraç otomatik tespiti için engine="python", sep=None
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    # kolon adlarını normalize et
    df.columns = (
        pd.Series(df.columns)
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
    )
    return df


def pick_col(df, candidates):
    """Aday kolon isimlerinden ilk bulduğunu döndür"""
    for c in candidates:
        if c in df.columns:
            return c
    return None


# ---------------- UI ----------------
st.set_page_config(page_title="Akıllı Katalog Analiz", layout="wide")
st.title("🧠 Akıllı Katalog Analiz")
st.caption("CSV/XLSX yükle; yazım, kategori, fiyat, stok, görsel ve kalite skoru hesapla.")

uploaded = st.file_uploader("CSV veya Excel yükleyin", type=["csv", "xlsx", "xls"])

if not uploaded:
    with st.expander("Örnek CSV/XLSX kolonları"):
        st.write(
            """
            Gerekli minimum kolonlar:
            - **title / başlık / ürün adı**
            - **category / kategori**
            
            İsteğe bağlı ama önerilir:
            - **subcategory (alt_kategori)**, **brand (marka)**, **price (fiyat)**, **stock (stok)**, **status (durum/statü)**, **image_url (görsel)**
            """
        )
    st.stop()

df = read_table(uploaded)

# Kolon eşleme
title_col  = pick_col(df, ["title","başlık","urun_adi","ürün adı","product_title","name"])
cat_col    = pick_col(df, ["category","kategori"])
subcat_col = pick_col(df, ["subcategory","sub_category","alt_kategori","alt kategori"])
brand_col  = pick_col(df, ["brand","marka"])
price_col  = pick_col(df, ["price","fiyat"])
stock_col  = pick_col(df, ["stock","stok"])
status_col = pick_col(df, ["status","statü","durum"])
img_col    = pick_col(df, ["image_url","image","image_path","görsel","gorsel","image link"])

# Minimum gereksinim kontrolü
if not title_col or not cat_col:
    st.error(
        f"Gerekli kolonlar bulunamadı.\n\n"
        f"Mevcut kolonlar: {list(df.columns)}\n\n"
        f"En azından **title**/**başlık** ve **category**/**kategori** olmalı."
    )
    st.stop()

rows = []
for _, r in df.iterrows():
    # --- Satır verilerini oku ---
    title = str(r.get(title_col, "") or "")
    input_category = str(r.get(cat_col, "") or "")
    subcat = str(r.get(subcat_col, "") or "") if subcat_col else ""
    brand  = str(r.get(brand_col, "") or "")  if brand_col  else ""
    price  = r.get(price_col, None)  if price_col  else None
    stock  = r.get(stock_col, None)  if stock_col  else None
    status = r.get(status_col, None) if status_col else None
    image_url = str(r.get(img_col, "") or "") if img_col else ""

    # --- Yazım kontrolleri ---
    spell_title = quick_spelling_checks(title)
    spell_sub   = quick_spelling_checks(subcat) if subcat else {"flags": [], "len": 0}
    spell_brand = quick_spelling_checks(brand)  if brand  else {"flags": [], "len": 0}

    # --- Kategori önerisi & görsel kontrolü ---
    suggested_category, _ = suggest_category(title, input_category)
    img_match = check_image_text_match_placeholder(title, image_url)

    # --- Kalite skoru (TÜM parametreler isimli) ---
    score, issue = compute_quality_score(
        spell=spell_title,
        input_category=input_category,
        suggested_category=suggested_category,
        img_match=img_match,
        price=price,
        stock=stock,
        status=status,
        sub_category=subcat,
        spell_sub=spell_sub,
        spell_brand=spell_brand,
        extra_spelling_issue=False,  # istersen True ya da kendi hesabın
    )

    # --- Sonuç satırı ---
    rows.append(
        {
            "title": title,
            "category": input_category,
            "subcategory": subcat,
            "brand": brand,
            "price": price,
            "stock": stock,
            "status": status,
            "image_path": image_url if image_url else None,
            "Recommended Category": suggested_category,
            "Kalite Skoru": score,
            "Analiz Sonucu": issue,
            "yazim_sorunu": bool(spell_title["flags"] or spell_sub["flags"] or spell_brand["flags"]),
        }
    )

out = pd.DataFrame(rows)

st.subheader("📊 Analiz Sonuçları")
st.dataframe(out, use_container_width=True)

st.download_button(
    "📥 Sonuçları CSV indir",
    out.to_csv(index=False).encode("utf-8"),
    "akilli_katalog_analiz_sonuclari.csv",
    "text/csv",
)

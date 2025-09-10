
import streamlit as st
import pandas as pd

from modules.spelling import quick_spelling_checks
from modules.category import suggest_category
from modules.scoring import compute_quality_score
from modules.vision import check_image_text_match_placeholder

st.set_page_config(page_title="Akıllı Katalog Analiz — Demo (v2)", layout="wide")
st.title("🧠 Otomatik Analiz")
st.caption("CSV/XLSX yükle, analiz et.")

def read_table(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    df.columns = (
        pd.Series(df.columns)
        .astype(str)
        .str.replace("\ufeff","", regex=False)
        .str.strip()
        .str.lower()
    )
    return df

def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

file = st.file_uploader("CSV veya Excel yükleyin", type=["csv","xlsx","xls"])
if not file:
    st.info("Başlamak için dosya yükleyin.")
    st.stop()

df = read_table(file)
title_col = pick_col(df, ["title","başlık","urun_adi","ürün adı","product_title","name"])
cat_col   = pick_col(df, ["category","kategori"])
subcat_col= pick_col(df, ["subcategory","sub_category","alt_kategori","alt kategori"])
brand_col = pick_col(df, ["brand","marka"])
price_col = pick_col(df, ["price","fiyat"])
stock_col = pick_col(df, ["stock","stok"])
status_col= pick_col(df, ["status","statü","durum"])
img_col   = pick_col(df, ["image_url","image","image_path","görsel","gorsel","image link"])

if not title_col or not cat_col:
    st.error(f"Gerekli sütun yok. Mevcut: {list(df.columns)}")
    st.stop()

rows = []
for _, r in df.iterrows():
    title = str(r.get(title_col,"") or "")
    input_category = str(r.get(cat_col,"") or "")
    subcat = str(r.get(subcat_col,"") or "") if subcat_col else ""
    brand  = str(r.get(brand_col,"") or "") if brand_col else ""
    price  = r.get(price_col, None) if price_col else None
    stock  = r.get(stock_col, None) if stock_col else None
    status = r.get(status_col, None) if status_col else None
    image_url = str(r.get(img_col,"") or "") if img_col else ""

    spell_title = quick_spelling_checks(title)
    spell_sub   = quick_spelling_checks(subcat) if subcat else {"flags":[],"len":0}
    spell_brand = quick_spelling_checks(brand) if brand else {"flags":[],"len":0}
    any_spelling_issue_other = bool(spell_sub["flags"] or spell_brand["flags"])

    suggested_category, cat_reason = suggest_category(title, input_category)
    img_match = check_image_text_match_placeholder(title, image_url)

    score, issue = compute_quality_score(
        spell=spell_title,
        input_category=input_category,
        suggested_category=suggested_category,
        img_match=img_match,
        price=price,
        stock=stock,
        status=status,
        sub_category=subcat,
        extra_spelling_issue=any_spelling_issue_other
    )

    rows.append({
        "title": title,
        "category": input_category,
        "subcategory": subcat,
        "brand": brand,
        "price": price,
        "stock": stock,
        "status": status,
        "image_path": image_url if image_url else None,
        "Recommended Category": suggested_category,
        "yazim_sorunu": bool(spell_title["flags"] or any_spelling_issue_other),
        "Kalite Skoru": score,
        "Analiz Sonucu": issue
    })

out = pd.DataFrame(rows)
st.dataframe(out, use_container_width=True)
st.download_button("📥 CSV indir", out.to_csv(index=False).encode("utf-8"),
                   "akilli_katalog_analiz_rapor.csv","text/csv")

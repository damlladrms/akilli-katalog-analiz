# app.py — Akıllı Katalog Analiz (önerili + görsel analizi)

import streamlit as st
import pandas as pd
import re

# Yerel modüller
from yazim_kontrol import quick_spelling_checks
from kategori_oneri import suggest_category
from kalite_skori import compute_quality_score
from gorsel_kontrol import analyze_image


# --- Yardımcılar ---
def read_table(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    df.columns = (
        pd.Series(df.columns)
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
    )
    return df

def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# Marka yazım kontrolü (kısalık/ALL CAPS cezası yok)
def brand_quick_check(text: str):
    t = (text or "").strip()
    flags = []
    if re.search(r"([A-Za-zÇĞİÖŞÜçğıöşü])\1{2,}", t): flags.append("char_repetition")
    if re.search(r"\s{2,}", t): flags.append("multi_space")
    return {"flags": flags, "len": len(t)}

# Basit öneriler
def suggest_title(title: str):
    if not title: return ""
    t = re.sub(r"([A-Za-zÇĞİÖŞÜçğıöşü])\1{2,}", r"\1", title)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t if t != title else ""

def suggest_subcategory(input_category, sub_category):
    SUB_OK = {
        "Elektronik":{"Kulaklık","Telefon","Bilgisayar","Aksesuar","Hoparlör"},
        "Giyim":{"Elbise","Tişört","Pantolon","Etek","Ceket","Mont","Gömlek"},
        "Ayakkabı":{"Spor Ayakkabı","Bot","Sandalet","Topuklu"},
    }
    cat = (input_category or "").strip()
    sub = (sub_category or "").strip()
    if not cat or cat not in SUB_OK or not sub: return ""
    if sub in SUB_OK[cat]: return ""
    for cand in SUB_OK[cat]:
        if cand.lower().split()[0] in sub.lower() or sub.lower().split()[0] in cand.lower():
            return cand
    return next(iter(SUB_OK[cat]))

def suggest_price(price):
    try:
        p = float(price)
        return "" if p > 0 else "Bir fiyat girin (>0)"
    except:
        return "Bir fiyat girin (>0)"

def suggest_stock(stock):
    try:
        s = float(stock)
        return "" if s >= 0 else "Stok bilgisini girin (≥0)"
    except:
        return "Stok bilgisini girin (≥0)"

def suggest_status(status, stock):
    stt = (str(status or "")).strip().lower()
    try: s = float(stock)
    except: s = None
    if stt in {"aktif","active"} and s == 0: return "Pasif"
    if stt in {"pasif","inactive"} and (s is not None and s > 0): return "Aktif"
    return ""

def suggest_image(img_dict, image_url):
    s = (img_dict or {}).get("status")
    if s == "missing": return "Görsel ekleyin (http… .jpg/.png)"
    if s == "invalid": return "URL http/https ile başlamalı"
    if s == "conflict": return "Başlığa uygun görsel kullanın"
    return ""


# --- UI ---
st.set_page_config(page_title="Akıllı Katalog Analiz", layout="wide")
st.title("🧠 Akıllı Katalog Analiz")
st.caption("CSV/XLSX yükle; yazım, kategori, fiyat, stok, görsel ve kalite skoru + öneriler.")

uploaded = st.file_uploader("CSV veya Excel yükleyin", type=["csv", "xlsx", "xls"])

if not uploaded:
    with st.expander("Örnek CSV/XLSX kolonları"):
        st.write(
            """
            Gerekli minimum kolonlar:
            - **title / başlık / ürün adı**
            - **category / kategori**
            
            İsteğe bağlı:
            - **subcategory (alt_kategori)**, **brand (marka)**, **price (fiyat)**, **stock (stok)**, **status (durum)**, **image_url (görsel)**
            """
        )
    st.stop()

df = read_table(uploaded)

# Kolon eşleme
title_col  = pick_col(df, ["title","başlık","urun_adi","ürün adı"])
cat_col    = pick_col(df, ["category","kategori"])
subcat_col = pick_col(df, ["subcategory","sub_category","alt_kategori"])
brand_col  = pick_col(df, ["brand","marka"])
price_col  = pick_col(df, ["price","fiyat"])
stock_col  = pick_col(df, ["stock","stok"])
status_col = pick_col(df, ["status","statü","durum"])
img_col    = pick_col(df, ["image_url","image","image_path","görsel"])

if not title_col or not cat_col:
    st.error(f"En azından **title**/**başlık** ve **category**/**kategori** olmalı.\n\nMevcut kolonlar: {list(df.columns)}")
    st.stop()

rows = []
for _, r in df.iterrows():
    title = str(r.get(title_col, "") or "")
    input_category = str(r.get(cat_col, "") or "")
    subcat = str(r.get(subcat_col, "") or "") if subcat_col else ""
    brand  = str(r.get(brand_col, "") or "")  if brand_col  else ""
    price  = r.get(price_col, None)  if price_col  else None
    stock  = r.get(stock_col, None)  if stock_col  else None
    status = r.get(status_col, None) if status_col else None
    image_url = str(r.get(img_col, "") or "") if img_col else ""

    spell_title = quick_spelling_checks(title)
    spell_sub   = quick_spelling_checks(subcat) if subcat else {"flags": [], "len": 0}
    spell_brand = brand_quick_check(brand) if brand else {"flags": [], "len": 0}

    suggested_category, _ = suggest_category(title, input_category)
    img_match = analyze_image(title, image_url)

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
        extra_spelling_issue=False,
        status_text=status,
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
        "Kalite Skoru": score,
        "Analiz Sonucu": issue,
        "Öneri Başlık": suggest_title(title),
        "Öneri Alt Kategori": suggest_subcategory(input_category, subcat),
        "Öneri Fiyat": suggest_price(price),
        "Öneri Stok": suggest_stock(stock),
        "Öneri Statü": suggest_status(status, stock),
        "Öneri Görsel": suggest_image(img_match, image_url),
    })

out = pd.DataFrame(rows)

st.subheader("📊 Analiz Sonuçları")
st.dataframe(out, use_container_width=True)

st.download_button(
    "📥 Sonuçları CSV indir",
    out.to_csv(index=False).encode("utf-8"),
    "akilli_katalog_analiz_sonuclari.csv",
    "text/csv",
)

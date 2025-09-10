import streamlit as st
import pandas as pd

# ŞİMDİLİK kökteki Türkçe dosyaları kullan
from yazim_kontrol import quick_spelling_checks
from kategori_oneri import suggest_category
from kalite_skori import compute_quality_score
from gorsel_kontrol import check_image_text_match_placeholder

# ---------------- Helpers (tek dosyada) ----------------

# Yazım kontrolü
def quick_spelling_checks(text: str):
    t = (text or "").strip()
    flags = []; L = len(t)
    if L == 0: return {"flags": [], "len": 0}
    if L < 5: flags.append("title_too_short")
    if L > 120: flags.append("title_too_long")
    if re.search(r"([A-Za-zÇĞİÖŞÜçğıöşü])\1{2,}", t): flags.append("char_repetition")
    if re.search(r"\s{2,}", t): flags.append("multi_space")
    if t.upper() == t and L >= 5: flags.append("all_caps")
    return {"flags": flags, "len": L}

# Basit kategori önerisi (keyword tabanlı)
KEYWORDS = {
    "Ayakkabı": ["ayakkabı","sneaker","bot","spor ayakkabı"],
    "Telefon": ["telefon","iphone","samsung","xiaomi","akıllı telefon"],
    "Bilgisayar": ["laptop","notebook","bilgisayar","macbook"],
    "Giyim": ["elbise","tişört","pantolon","etek","ceket","mont","gömlek"],
    "Ev & Yaşam": ["tabak","bardak","yastık","havlu","çarşaf","tencere"],
}
def suggest_category(title: str, input_category: str):
    t = (title or "").lower()
    scores = {cat: sum(1 for k in kws if k in t) for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return input_category or "Belirsiz", "Anahtar kelime bulunamadı."
    if input_category and best != input_category:
        return best, f"Mevcut: {input_category} → Öneri: {best}"
    return input_category or best, "OK"

# Görsel–başlık (placeholder)
def check_image_text_match_placeholder(title: str, image_url: str):
    title_ok = len((title or "").strip()) >= 5
    url_ok = bool(image_url) and str(image_url).startswith("http")
    return {"match": bool(title_ok and url_ok)}

# Alt kategori sözlüğü
SUB_OK = {
    "Elektronik": {"Kulaklık","Telefon","Bilgisayar","Aksesuar","Hoparlör"},
    "Giyim": {"Elbise","Tişört","Pantolon","Etek","Ceket","Mont","Gömlek"},
    "Ayakkabı": {"Spor Ayakkabı","Bot","Sandalet","Topuklu"},
}

# Skor + issue
def compute_quality_score(
    spell, input_category, suggested_category, img_match,
    price=None, stock=None, status=None, sub_category=None,
    spell_sub=None, spell_brand=None
):
    score = 100; flags = []

    penalties = {"title_too_short":15,"title_too_long":10,"char_repetition":10,"all_caps":5,"multi_space":5}
    for f in (spell.get("flags", []) if spell else []):
        score -= penalties.get(f, 0); flags.append(f)

    if spell_sub and spell_sub.get("flags"): score -= 8; flags.append("subcategory_spelling")
    if spell_brand and spell_brand.get("flags"): score -= 5; flags.append("brand_spelling")

    if input_category and suggested_category and input_category != suggested_category:
        score -= 20; flags.append("category_mismatch")

    if sub_category:
        cat = (input_category or "").strip(); sub = (sub_category or "").strip()
        if cat in SUB_OK and sub and sub not in SUB_OK[cat]:
            score -= 15; flags.append("subcategory_mismatch")

    if not img_match.get("match", False):
        score -= 20; flags.append("image_text_mismatch")

    try:
        p = float(price) if price not in (None, "") else None
    except: p = None
    if p is None or p <= 0:
        score -= 15; flags.append("invalid_price")

    try:
        s = float(stock) if stock not in (None, "") else None
    except: s = None
    if s is None or s < 0:
        score -= 10; flags.append("invalid_stock")

    stt = (str(status or "")).strip().lower()
    if stt in {"aktif","active"} and (s is not None and s == 0):
        score -= 10; flags.append("active_but_out_of_stock")

    score = max(0, min(100, score))
    issue = "Sorun yok." if not flags else " | ".join(sorted(set(flags)))
    return score, issue

# Öneriler
def _fix_rep(text): return re.sub(r'([A-Za-zÇĞİÖŞÜçğıöşü])\1{2,}', r'\1', text or "")
def suggest_title(title): 
    t = (title or "").strip()
    if not t: return t
    t = _fix_rep(t); t = re.sub(r"\s{2,}", " ", t); return t.strip()
def suggest_subcategory(input_category, sub_category):
    cat = (input_category or "").strip(); sub = (sub_category or "").strip()
    if not cat or cat not in SUB_OK or not sub: return sub
    if sub in SUB_OK[cat]: return sub
    low = sub.lower()
    for cand in SUB_OK[cat]:
        if cand.lower().split()[0] in low or low.split()[0] in cand.lower(): return cand
    return next(iter(SUB_OK[cat]))
def suggest_price(price):
    try: p = float(price); 
    except: p = None
    return p if (p and p>0) else "Bir fiyat girin (>0)"
def suggest_stock(stock):
    try: s = float(stock)
    except: s = None
    return int(s) if (s is not None and s>=0) else "Stok bilgisini girin (≥0)"
def suggest_status(status, stock):
    stt = (str(status or "")).strip().lower()
    try: s = float(stock)
    except: s = None
    if stt in {"aktif","active"} and s == 0: return "Pasif"
    if stt in {"pasif","inactive"} and (s is not None and s>0): return "Aktif"
    return status or "Aktif/Pasif"
def suggest_image(image_url):
    u = (str(image_url) or "").strip()
    return u if u.startswith("http") else "Geçerli bir görsel URL ekleyin (http...)"

# CSV/XLSX oku
def read_table(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    df.columns = (pd.Series(df.columns).astype(str)
                  .str.replace("\ufeff","", regex=False).str.strip().str.lower())
    return df

def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns: return c
    return None

# ---------------- UI ----------------
st.set_page_config(page_title="Akıllı Katalog Analiz — Tek Dosya", layout="wide")
st.title("🧠 Otomatik Analiz + Öneriler")
st.caption("Tek dosya sürümü. CSV/XLSX yükle; yazım, kategori/alt kategori, fiyat, stok, görsel kontrolleri ve önerileri gör.")

file = st.file_uploader("CSV veya Excel yükleyin", type=["csv","xlsx","xls"])
if not file:
    st.info("Başlamak için bir dosya yükleyin.")
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
    st.error(f"Gerekli sütunlar bulunamadı. Mevcut: {list(df.columns)}\n"
             f"En azından title|başlık ve category|kategori olmalı.")
    st.stop()

rows = []
for _, r in df.iterrows():
    title = str(r.get(title_col, "") or "")
    input_category = str(r.get(cat_col, "") or "")
    subcat = str(r.get(subcat_col, "") or "") if subcat_col else ""
    brand  = str(r.get(brand_col, "") or "") if brand_col else ""
    price  = r.get(price_col, None) if price_col else None
    stock  = r.get(stock_col, None) if stock_col else None
    status = r.get(status_col, None) if status_col else None
    image_url = str(r.get(img_col, "") or "") if img_col else ""

    spell_title = quick_spelling_checks(title)
    spell_sub   = quick_spelling_checks(subcat) if subcat else {"flags": [], "len": 0}
    spell_brand = quick_spelling_checks(brand)  if brand  else {"flags": [], "len": 0}

    suggested_category, _ = suggest_category(title, input_category)
    img_match = check_image_text_match_placeholder(title, image_url)

    score, issue = compute_quality_score(
        spell=spell_title, input_category=input_category,
        suggested_category=suggested_category, img_match=img_match,
        price=price, stock=stock, status=status, sub_category=subcat,
        spell_sub=spell_sub, spell_brand=spell_brand
    )

    # Öneriler
    title_suggestion = suggest_title(title)
    subcategory_suggestion = suggest_subcategory(input_category, subcat) if (subcat or input_category) else subcat
    price_suggestion = suggest_price(price)
    stock_suggestion = suggest_stock(stock)
    status_suggestion = suggest_status(status, stock)
    image_suggestion = suggest_image(image_url)

    rows.append({
        "title": title, "category": input_category, "subcategory": subcat, "brand": brand,
        "price": price, "stock": stock, "status": status, "image_path": image_url or None,
        "Recommended Category": suggested_category,
        "yazim_sorunu": bool(spell_title["flags"] or spell_sub["flags"] or spell_brand["flags"]),
        "Kalite Skoru": score, "Analiz Sonucu": issue,
        "Öneri Başlık": title_suggestion if title_suggestion != title else "",
        "Öneri Kategori": suggested_category if input_category != suggested_category else "",
        "Öneri Alt Kategori": subcategory_suggestion if subcategory_suggestion and subcategory_suggestion != subcat else "",
        "Öneri Fiyat": price_suggestion if isinstance(price_suggestion, str) else "",
        "Öneri Stok": stock_suggestion if isinstance(stock_suggestion, str) else "",
        "Öneri Statü": status_suggestion if status_suggestion and (status_suggestion != (status or "")) else "",
        "Öneri Görsel": image_suggestion if isinstance(image_suggestion, str) and image_suggestion.startswith("Geçerli") else ""
    })

out = pd.DataFrame(rows)
st.dataframe(out, use_container_width=True)
st.download_button("📥 CSV indir", out.to_csv(index=False).encode("utf-8"),
                   "akilli_katalog_analiz_rapor.csv","text/csv")

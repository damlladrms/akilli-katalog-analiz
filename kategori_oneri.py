
def kategori_tahmin_et(title):
    title = title.lower()
    if "ayakkabı" in title:
        return "Ayakkabı"
    elif "elbis" in title:
        return "Giyim"
    elif "kulaklık" in title:
        return "Elektronik"
    elif "mont" in title:
        return "Giyim"
    return "Diğer"
    # kategori_oneri.py

KEYWORDS = {
    "Ayakkabı": ["ayakkabı", "sneaker", "bot", "spor ayakkabı"],
    "Telefon": ["telefon", "iphone", "samsung", "xiaomi", "akıllı telefon"],
    "Bilgisayar": ["laptop", "notebook", "bilgisayar", "macbook"],
    "Giyim": ["elbise", "tişört", "pantolon", "etek", "ceket", "mont", "gömlek"],
    "Ev & Yaşam": ["tabak", "bardak", "yastık", "havlu", "çarşaf", "tencere"],
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

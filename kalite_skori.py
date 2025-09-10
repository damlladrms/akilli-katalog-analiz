# kalite_skori.py

def compute_quality_score(spell, input_category, suggested_category, img_match,
                          price=None, stock=None, status=None, sub_category=None,
                          spell_sub=None, spell_brand=None):
    score = 100
    flags = []

    # Yazım sorunları
    for f in (spell.get("flags", []) if spell else []):
        score -= 10
        flags.append(f)

    # Kategori uyumsuzluğu
    if input_category and suggested_category and input_category != suggested_category:
        score -= 20
        flags.append("category_mismatch")

    # Görsel uyumu
    if not img_match.get("match", False):
        score -= 20
        flags.append("image_text_mismatch")

    # Fiyat kontrolü
    try:
        p = float(price) if price not in (None, "") else None
    except:
        p = None
    if p is None or p <= 0:
        score -= 15
        flags.append("invalid_price")

    # Stok kontrolü
    try:
        s = float(stock) if stock not in (None, "") else None
    except:
        s = None
    if s is None or s < 0:
        score -= 10
        flags.append("invalid_stock")

    return max(0, score), "Sorun yok." if not flags else " | ".join(sorted(set(flags)))

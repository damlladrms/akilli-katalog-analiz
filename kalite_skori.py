# kalite_skori.py

def compute_quality_score(
    spell, input_category, suggested_category, img_match,
    price=None, stock=None, status=None, sub_category=None,
    spell_sub=None, spell_brand=None,
    extra_spelling_issue=False,
    status_text=None,
    **kwargs
):
    score = 100
    flags = []

    # --- Başlık yazım sorunları ---
    penalties = {
        "title_too_short": 15,
        "title_too_long": 10,
        "char_repetition": 10,
        "all_caps": 5,
        "multi_space": 5,
    }
    for f in (spell.get("flags", []) if spell else []):
        score -= penalties.get(f, 0)
        flags.append(f)

    # --- Alt kategori / marka yazım sorunları ---
    if spell_sub and spell_sub.get("flags"):
        score -= 8
        flags.append("subcategory_spelling")
    if spell_brand and spell_brand.get("flags"):
        score -= 5
        flags.append("brand_spelling")

    # Diğer alanlardan yazım uyarısı
    if extra_spelling_issue:
        score -= 8
        flags.append("spelling_issue_other_fields")

    # --- Kategori uyumsuzluğu ---
    if input_category and suggested_category and input_category != suggested_category:
        score -= 20
        flags.append("category_mismatch")

    # --- Alt kategori uyumu ---
    SUB_OK = {
        "Elektronik": {"Kulaklık", "Telefon", "Bilgisayar", "Aksesuar", "Hoparlör"},
        "Giyim": {"Elbise", "Tişört", "Pantolon", "Etek", "Ceket", "Mont", "Gömlek"},
        "Ayakkabı": {"Spor Ayakkabı", "Bot", "Sandalet", "Topuklu"},
    }
    if sub_category:
        cat = (input_category or "").strip()
        sub = (sub_category or "").strip()
        if cat in SUB_OK and sub and sub not in SUB_OK[cat]:
            score -= 15
            flags.append("subcategory_mismatch")

    # --- Görsel puanlama ---
    img_status = (img_match or {}).get("status")
    if img_status == "missing":
        score -= 10
        flags.append("missing_image")
    elif img_status == "invalid":
        score -= 15
        flags.append("invalid_image_url")
    elif img_status == "conflict":
        score -= 20
        flags.append("image_text_mismatch")
    # ok → ceza yok

    # --- Fiyat kontrolü ---
    try:
        p = float(price) if price not in (None, "") else None
    except Exception:
        p = None
    if p is None or p <= 0:
        score -= 15
        flags.append("invalid_price")

    # --- Stok kontrolü ---
    try:
        s = float(stock) if stock not in (None, "") else None
    except Exception:
        s = None
    if s is None or s < 0:
        score -= 10
        flags.append("invalid_stock")

    # --- Statü–stok tutarlılığı ---
    st_txt = (str(status_text if status_text is not None else status) or "").strip().lower()
    if st_txt in {"aktif", "active"} and (s is not None and s == 0):
        score -= 10
        flags.append("active_but_out_of_stock")

    # --- Sonuç ---
    score = max(0, min(100, score))
    issue = "Sorun yok." if not flags else " | ".join(sorted(set(flags)))
    return score, issue

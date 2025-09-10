
def compute_quality_score(
    spell: dict, input_category: str, suggested_category: str, img_match: dict,
    price=None, stock=None, status=None, sub_category=None,
    extra_spelling_issue: bool = False
):
    score = 100
    flags = []

    penalties = {
        "title_too_short": 15,
        "title_too_long": 10,
        "char_repetition": 10,
        "all_caps": 5,
        "multi_space": 5
    }
    for f in spell.get("flags", []):
        score -= penalties.get(f, 0)
        flags.append(f)

    if extra_spelling_issue:
        score -= 8
        flags.append("spelling_issue_other_fields")

    if input_category and suggested_category and input_category != suggested_category:
        score -= 20
        flags.append("category_mismatch")

    SUB_OK = {
        "Elektronik": {"Kulaklık","Telefon","Bilgisayar","Aksesuar","Hoparlör"},
        "Giyim": {"Elbise","Tişört","Pantolon","Etek","Ceket","Mont"},
    }
    if sub_category:
        cat = (input_category or "").strip()
        sub = (sub_category or "").strip()
        if cat in SUB_OK and sub and sub not in SUB_OK[cat]:
            score -= 15
            flags.append("subcategory_mismatch")

    if not img_match.get("match", False):
        score -= 20
        flags.append("image_text_mismatch")

    try:
        p = float(price) if price not in (None, "") else None
    except:
        p = None
    if p is None or p <= 0:
        score -= 15
        flags.append("invalid_price")

    try:
        s = float(stock) if stock not in (None, "") else None
    except:
        s = None
    if s is None or s < 0:
        score -= 10
        flags.append("invalid_stock")

    st = (str(status or "")).strip().lower()
    if st in {"aktif","active"} and s is not None and s == 0:
        score -= 10
        flags.append("active_but_out_of_stock")

    score = max(0, min(100, score))
    issue = "Sorun yok." if not flags else " | ".join(sorted(set(flags)))
    return score, issue

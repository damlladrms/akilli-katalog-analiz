# kalite_skori.py

def compute_quality_score(
    spell, input_category, suggested_category, img_match,
    price=None, stock=None, status=None, sub_category=None,
    spell_sub=None, spell_brand=None,
    extra_spelling_issue=False,   # app.py'den gelebilir
    **kwargs                      # ileride yeni parametre gelirse hata vermesin
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
    if spell_sub and spell_sub

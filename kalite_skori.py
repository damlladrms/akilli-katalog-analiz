# kalite_skori.py

def compute_quality_score(spell, input_category, suggested_category, img_match,
                          price=None, stock=None, status=None, sub_category=None,
                          spell_sub=None, spell_brand=None,
                          extra_spelling_issue=False, **kwargs):
    score = 100
    flags = []

    # Yazım sorunları (başlık)
    for f in (spell.get("flags", []) if spell else []):
        score -= 10
        flags.append(f)

    # Alt kategori / marka yazım sorunları
    if spell_sub and spell_sub.get("flags"):
        score -= 8
        flags.append("subcategory_spelling")
    if spell_brand and spell_brand.get("flags"):
        score -= 5
        flags.append("brand_spelling")

    # Diğer alanlardan gelen toplu yazım işareti
    if extra_spelling_issue:
        score -= 8
        flags.append("spelling_issue_other_fields")

    # Kategori uyumsuzluğu
    if input_category and suggested_category and input_category != suggested_category:
        score -= 20
        flags.append("category_mismatch")

    # Görsel uyumu (placeholder kontrol)
  if not img_match.get("match", False):
    score -= 20
    flags.append("image_text_mismatch")

# kalite_skori.py

def compute_quality_score(spell, input_category, suggested_category, img_match,
                          price=None, stock=None, status=None, sub_category=None,
                          spell_sub=None, spell_brand=None,
                          extra_spelling_issue=False, **kwargs):
    score = 100
    flags = []

    # Yazım sorunları (başlık)
    for f in (spell.get("flags", []) if spell else []):
        score -= 10
        flags.append(f)

    # Alt kategori / marka yazım sorunları
    if spell_sub and spell_sub.get("flags"):
        score -= 8
        flags.append("subcategory_spelling")
    if spell_brand and spell_brand.get("flags"):
        score -= 5
        flags.append("brand_spelling")

    # Diğer alanlardan gelen toplu yazım işareti
    if extra_spelling_issue:
        score -= 8
        flags.append("spelling_issue_other_fields")

    # Kategori uyumsuzluğu
    if input_category and suggested_category and input_category != suggested_category:
        score -= 20
        flags.append("category_mismatch")

    # Görsel uyumu (placeholder kontrol)
    if not img_matc_

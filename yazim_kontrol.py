import re

def quick_spelling_checks(text: str):
    t = (text or "").strip()
    flags = []
    L = len(t)

    if L == 0:
        return {"flags": [], "len": 0}

    if L < 5:
        flags.append("title_too_short")
    if L > 120:
        flags.append("title_too_long")
    if re.search(r"([A-Za-zÇĞİÖŞÜçğıöşü])\1{2,}", t):
        flags.append("char_repetition")
    if re.search(r"\s{2,}", t):
        flags.append("multi_space")
    if t.upper() == t and L >= 5:
        flags.append("all_caps")

    return {"flags": flags, "len": L}


def hesapla(row):
    score = 100
    if row["yazim_sorunu"]:
        score -= 20
    if row["kategori_uyusmazligi"]:
        score -= 30
    if row["gorsel_durumu"] != "iyi":
        score -= 30
    return max(score, 0)

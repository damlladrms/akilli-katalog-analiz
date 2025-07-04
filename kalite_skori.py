def kalite_skoru_hesapla(row):
    score = 100
    if row["kategori_uyusmazligi"]:
        score -= 30
    if row["yazim_sorunu"]:
        score -= 20
    if row["gorsel_durumu"] != "İyi":
        score -= 50
    return max(score, 0)
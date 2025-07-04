
def kalite_puani_hesapla(row):
    puan = 100
    if row.get("yazim_sorunu"):
        puan -= 20
    if row.get("kategori_uyusmazligi"):
        puan -= 30
    if row.get("price") and row["price"] < 50:
        puan -= 10
    if row.get("stock") and row["stock"] < 10:
        puan -= 10
    return max(puan, 0)
    
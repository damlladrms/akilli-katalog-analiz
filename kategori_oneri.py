
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
    
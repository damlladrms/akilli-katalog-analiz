def kategori_tahmin_et(title):
    title = title.lower()
    if any(x in title for x in ["ayakkabı", "sneaker", "bot"]):
        return "Ayakkabı"
    elif any(x in title for x in ["elbise", "ceket", "mont", "gömlek", "pantolon"]):
        return "Giyim"
    elif any(x in title for x in ["telefon", "kulaklık", "laptop"]):
        return "Elektronik"
    else:
        return "Diğer"
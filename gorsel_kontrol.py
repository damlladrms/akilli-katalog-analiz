import os

def gorsel_kalite_kontrolu(path):
    if not path or not isinstance(path, str):
        return "Eksik"
    elif "bozuk" in path.lower() or "hata" in path.lower():
        return "Bozuk"
    elif path.lower().endswith((".jpg", ".jpeg", ".png")):
        return "İyi"
    else:
        return "Format Dışı"
# gorsel_kontrol.py

def check_image_text_match_placeholder(title: str, image_url: str):
    """
    Basit placeholder kontrolü:
    - Başlık en az 5 karakter olmalı
    - Görsel URL'si 'http' ile başlamalı
    """
    title_ok = len((title or "").strip()) >= 5
    url_ok = bool(image_url) and str(image_url).startswith("http")
    return {"match": bool(title_ok and url_ok)}

# gorsel_kontrol.py

def check_image_text_match_placeholder(title: str, image_url: str):
    """
    Basit kontrol: 
    - Başlık en az 5 karakter olacak
    - Görsel URL'si 'http' ile başlayacak
    """
    title_ok = len((title or "").strip()) >= 5
    url_ok = bool(image_url) and str(image_url).startswith("http")
    return {"match": bool(title_ok and url_ok)}

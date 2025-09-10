
def check_image_text_match_placeholder(title: str, image_url: str):
    title_ok = len((title or "").strip()) >= 5
    url_ok = bool(image_url) and image_url.startswith("http")
    if title_ok and url_ok:
        return {"match": True, "reason": "Basit kontrol: başlık+URL var"}
    return {"match": False, "reason": "Eksik başlık veya geçersiz URL"}

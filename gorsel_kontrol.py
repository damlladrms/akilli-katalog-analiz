# gorsel_kontrol.py

def analyze_image(title: str, image_url: str):
    """
    Görseli 4 duruma ayırır:
    - missing  : görsel yok
    - invalid  : URL http/https ile başlamıyor
    - conflict : görsel dosya adındaki anahtar kelime başlıkla çelişiyor
    - ok       : sorun yok / ceza yok
    """
    t = (title or "").lower().strip()
    u = (image_url or "").strip()

    if not u:
        return {"status": "missing", "match": False, "reason": "no_image"}

    if not u.startswith(("http://", "https://")):
        return {"status": "invalid", "match": False, "reason": "invalid_url"}

    # Basit anahtar kelime kontrolü (dosya adı)
    fname = u.split("/")[-1].lower()
    keywords = ["ayakkabı", "elbise", "kulaklık", "mont", "telefon", "laptop"]
    hits_title = {k for k in keywords if k in t}
    hits_image = {k for k in keywords if k in fname}

    if hits_title and hits_image and hits_title.isdisjoint(hits_image):
        return {"status": "conflict", "match": False, "reason": "keyword_conflict"}

    return {"status": "ok", "match": True, "reason": "ok"}

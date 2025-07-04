
def kontrol_et(url):
    if not url or not isinstance(url, str):
        return "boş"
    elif "placeholder" in url or "default.jpg" in url:
        return "bozuk"
    return "iyi"

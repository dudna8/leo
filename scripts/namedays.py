import requests

def ziskaj_meniny():
    """Získa dnešné meniny pre Slovensko pomocou verejného API."""
    url = "https://nameday.abalin.net/api/V1/today?country=sk"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        # API vracia mená v objekte nameday pod kľúčom 'sk'
        return data.get('nameday', {}).get('sk', "Neznáme")
    except Exception:
        return "Neznáme"
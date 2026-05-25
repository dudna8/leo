import requests
from datetime import date

def ziskaj_predpoved_bratislava(target_date=None):
    """
    Stiahne hodinovú predpoveď z Open-Meteo API pre Bratislavu
    pre zadaný dátum.
    """
    if target_date is None:
        target_date = date.today()

    today = date.today()
    days_diff = (target_date - today).days

    # Súradnice pre Bratislavu
    latitude = 48.1486
    longitude = 17.1077
    
    # Parametre požiadavky: hodinová predpoveď, teplota a kód počasia
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "weather_code"],
        "timezone": "Europe/Berlin", # Nastavenie časového pásma pre správne indexovanie hodín
        "forecast_days": days_diff + 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Skontroluje, či požiadavka prebehla v poriadku
        data = response.json()
        
        hourly_data = data.get("hourly", {})
        teploty = hourly_data.get("temperature_2m", [])
        kody_pocasia = hourly_data.get("weather_code", [])
        
        # Jednoduchý slovník na interpretáciu WMO kódov počasia
        wmo_popis = {
            0: "Jasno",
            1: "Prevažne jasno",
            2: "Polooblačno",
            3: "Zamračené",
            45: "Hmla",
            51: "Slabé mrholenie",
            61: "Slabý dážď",
            71: "Slabé sneženie",
            80: "Prehánky",
            95: "Búrka"
        }

        # Mapovanie WMO kódov na Bootstrap Icons triedy
        wmo_ikony = {
            0: "bi-sun",
            1: "bi-cloud-sun",
            2: "bi-cloud-sun",
            3: "bi-cloud",
            45: "bi-cloud-fog",
            51: "bi-cloud-drizzle",
            61: "bi-cloud-rain",
            71: "bi-cloud-snow",
            80: "bi-cloud-rain-heavy",
            95: "bi-cloud-lightning-rain"
        }
        
        # Výber konkrétnych hodín (indexy 7, 12, 16 zodpovedajú daným hodinám dňa)
        vybrane_casy = [7, 12, 16]
        vysledky = []
        
        for hodina in vybrane_casy:
            # Index v poli: (počet dní od dnes * 24 hodín) + konkrétna hodina
            idx = (days_diff * 24) + hodina
            if idx < len(teploty):
                kod = kody_pocasia[idx]
                vysledky.append({
                    "cas": f"{hodina}:00",
                    "teplota": f"{teploty[idx]}°C",
                    "stav": wmo_popis.get(kod, "Neznáme"),
                    "ikona": wmo_ikony.get(kod, "bi-question-circle")
                })
        
        return vysledky

    except requests.exceptions.RequestException as e:
        return {"error": f"Nepodarilo sa spojiť s API: {e}"}

# Príklad spustenia
if __name__ == "__main__":
    predpoved = ziskaj_predpoved_bratislava()
    if "error" in predpoved:
        print(predpoved["error"])
    else:
        for cas, info in predpoved.items():
            print(f"Čas {cas}: {info['teplota']}, {info['stav']}")

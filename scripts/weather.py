import requests

def ziskaj_predpoved_bratislava():
    """
    Stiahne hodinovú predpoveď z Open-Meteo API pre Bratislavu
    a vytiahne teplotu a podmienky pre 7:00, 12:00 a 16:00.
    """
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
        "forecast_days": 1
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
        
        # Výber konkrétnych hodín (indexy 7, 12, 16 zodpovedajú daným hodinám dňa)
        vybrane_casy = [7, 12, 16]
        vysledky = {}
        
        for hodina in vybrane_casy:
            if hodina < len(teploty):
                vysledky[f"{hodina}:00"] = {
                    "teplota": f"{teploty[hodina]}°C",
                    "stav": wmo_popis.get(kody_pocasia[hodina], f"Kód {kody_pocasia[hodina]}")
                }
        
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

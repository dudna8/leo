from flask import Flask, render_template
import logging
from datetime import datetime, timedelta
import sys
import os

# Pridanie koreňového adresára do cesty pre istotu, ak by Gunicorn štartoval z iného miesta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Nastavenie logovania do konzoly (uvidíš v journalctl)
logging.basicConfig(level=logging.INFO)

try:
    from scripts.weather import ziskaj_predpoved_bratislava
    from scripts.kindergarden import ziskaj_dnesny_obed
    from scripts.school_calendar import ziskaj_udalosti
except ImportError as e:
    app.logger.error(f"KRITICKÁ CHYBA IMPORTU: {e}")
    # Definujeme náhradné funkcie, aby Flask aspoň naštartoval a vyhol sa 502
    ziskaj_predpoved_bratislava = lambda td: None
    ziskaj_dnesny_obed = lambda td: [{"typ": "Chyba", "nazov": "Chyba pri načítaní skriptov."}]
    ziskaj_udalosti = lambda: []

@app.route('/')
def home():
    pocasie = None
    obed = [{"typ": "Info", "nazov": "Informácie o obede nie sú dostupné."}]
    udalosti = []

    # Logika pre výber dňa
    now = datetime.now()
    target_date = now.date()

    # Ak je po 16:00, pozeráme sa na ďalší deň
    if now.hour >= 16:
        target_date += timedelta(days=1)

    # Ak je cieľový deň víkend, posunieme sa na pondelok
    while target_date.weekday() >= 5:  # 5 = Sobota, 6 = Nedeľa
        target_date += timedelta(days=1)

    # Zistíme, či zobrazujeme dnešný deň
    je_dnes = target_date == now.date()

    try:
        pocasie = ziskaj_predpoved_bratislava(target_date)
    except Exception as e:
        app.logger.error(f"Chyba pocasie: {e}")

    try:
        obed = ziskaj_dnesny_obed(target_date)
    except Exception as e:
        app.logger.error(f"Chyba obed: {e}")

    try:
        udalosti = ziskaj_udalosti()
    except Exception as e:
        app.logger.error(f"Chyba kalendar: {e}")

    # Formátovanie dátumu pre zobrazenie v hlavičke (napr. Pondelok 20.05.2024)
    dni = ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"]
    datum_zobrazenia = f"{dni[target_date.weekday()]} {target_date.strftime('%d.%m.%Y')}"

    return render_template('index.html', 
                           pocasie=pocasie, 
                           obed=obed, 
                           udalosti=udalosti,
                           datum_zobrazenia=datum_zobrazenia,
                           je_dnes=je_dnes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
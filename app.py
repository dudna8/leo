from flask import Flask, render_template
import logging
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
    ziskaj_predpoved_bratislava = lambda: None
    ziskaj_dnesny_obed = lambda: ["Chyba pri načítaní skriptov."]
    ziskaj_udalosti = lambda: []

@app.route('/')
def home():
    pocasie = None
    obed = ["Informácie o obede nie sú dostupné."]
    udalosti = []

    try:
        pocasie = ziskaj_predpoved_bratislava()
    except Exception as e:
        app.logger.error(f"Chyba pocasie: {e}")

    try:
        obed = ziskaj_dnesny_obed()
    except Exception as e:
        app.logger.error(f"Chyba obed: {e}")

    try:
        udalosti = ziskaj_udalosti()
    except Exception as e:
        app.logger.error(f"Chyba kalendar: {e}")
    
    return render_template('index.html', 
                           pocasie=pocasie, 
                           obed=obed, 
                           udalosti=udalosti)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
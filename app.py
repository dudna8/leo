from flask import Flask, render_template
import logging
from scripts.weather import ziskaj_predpoved_bratislava
from scripts.kindergarden import ziskaj_dnesny_obed
from scripts.school_calendar import ziskaj_udalosti

app = Flask(__name__)

# Nastavenie logovania do konzoly (uvidíš v journalctl)
logging.basicConfig(level=logging.INFO)

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
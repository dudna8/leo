from flask import Flask, render_template
from weather import ziskaj_predpoved_bratislava
from kindergarden import ziskaj_dnesny_obed
from school_calendar import ziskaj_udalosti

app = Flask(__name__)

@app.route('/')
def home():
    # Získanie dát s jednoduchým ošetrením chýb
    try:
        pocasie = ziskaj_predpoved_bratislava()
    except Exception:
        pocasie = None

    try:
        obed = ziskaj_dnesny_obed()
    except Exception:
        obed = ["Nepodarilo sa načítať jedálny lístok."]

    try:
        udalosti = ziskaj_udalosti()
    except Exception:
        udalosti = []
    
    return render_template('index.html', 
                           pocasie=pocasie, 
                           obed=obed, 
                           udalosti=udalosti)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta


def ziskaj_udalosti():
    url = "https://msborska.edupage.org/calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Mapa slovenských mesiacov na čísla
    mesiace_map = {
        "Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, 
        "Máj": 5, "Jún": 6, "Júl": 7, "August": 8, 
        "September": 9, "Október": 10, "November": 11, "December": 12
    }
    
    today = datetime.now().date()

    # Logika pre posun zobrazenia: ak je dnes víkend, hľadáme až od pondelka
    zobrazit_od = today
    if today.weekday() >= 5:  # 5 = Sobota, 6 = Nedeľa
        dni_do_pondelka = 7 - today.weekday()
        zobrazit_od = today + timedelta(days=dni_do_pondelka)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "calendar.json")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        events = []

        # Tvoj HTML kód ukázal, že celý kalendár je v <ul> s triedou 'skgdCalendar'
        calendar_list = soup.find("ul", class_=lambda x: x and "skgdCalendar" in x)

        if calendar_list:
            current_month = ""
            
            # Prejdeme všetky priame <li> elementy (riadky) v tomto zozname
            for li in calendar_list.find_all("li", recursive=False):
                
                # 1. Je to nadpis mesiaca? (Podľa tvojho kódu: calendar_DFText_1)
                month_el = li.find(class_=lambda x: x and "calendar_DFText_1" in x)
                if month_el:
                    current_month = month_el.get_text(strip=True).capitalize()
                    continue
                
                # 2. Je to udalosť? 
                # Deň: calendar_DFText_2, Skratka: calendar_DFText_3, Text: calendar_DFText_4
                day_num_el = li.find(class_=lambda x: x and "calendar_DFText_2" in x)
                day_name_el = li.find(class_=lambda x: x and "calendar_DFText_3" in x)
                title_el = li.find(class_=lambda x: x and "calendar_DFText_4" in x)
                
                if day_num_el and title_el:
                    day_num = day_num_el.get_text(strip=True)
                    
                    # Názov môže obsahovať <br>, takže to elegantne spojíme s čiarou
                    title_text = title_el.get_text(separator=" | ", strip=True)
                    
                    # Logika pre výpočet zostávajúcich dní
                    m_num = mesiace_map.get(current_month, today.month)
                    year = today.year
                    
                    # Ak je mesiac udalosti menší ako aktuálny mesiac, pravdepodobne ide o budúci rok
                    if m_num < today.month:
                        year += 1
                    
                    try:
                        event_date = date(year, m_num, int(day_num))
                        
                        # NEUKAZOVAT VECI KTORE UZ BOLI (alebo sú cez víkend, ak je dnes víkend)
                        if event_date < zobrazit_od:
                            continue
                            
                        diff = (event_date - today).days
                        
                        if diff == 0:
                            ostava = "dnes"
                        elif diff == 1:
                            ostava = "zajtra"
                        elif 1 < diff < 5:
                            ostava = f"o {diff} dni"
                        else:
                            ostava = f"o {diff} dní"
                            
                        cas_display = f"{day_num}.{m_num}."
                    except ValueError:
                        continue

                    events.append({
                        "cas": cas_display,
                        "ostava": ostava,
                        "nazov": title_text
                    })

        if not events:
            events = [
                {
                    "cas": "Info",
                    "nazov": "Momentálne nie sú v kalendári žiadne nadchádzajúce udalosti."
                }
            ]

        # Obmedzíme počet zobrazených udalostí na 5 najnovších
        events = events[:5]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=4)

        print("✓ Kalendár úspešne stiahnutý pomocou priamych tried z HTML!")
        return events

    except Exception as e:
        print(f"Chyba pri scrapovaní: {e}")
        return []

if __name__ == "__main__":
    ziskaj_udalosti()
import json
import os
import requests
from bs4 import BeautifulSoup


def get_calendar():
    url = "https://msborska.edupage.org/calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

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
                    day_name = day_name_el.get_text(strip=True) if day_name_el else ""
                    
                    # Názov môže obsahovať <br>, takže to elegantne spojíme s čiarou
                    title_text = title_el.get_text(separator=" | ", strip=True)
                    
                    full_date = f"{day_num}. {day_name} ({current_month})"
                    events.append({
                        "datum": full_date,
                        "nazov": title_text
                    })

        if not events:
            events = [
                {
                    "datum": "Info",
                    "nazov": "Momentálne nie sú v kalendári žiadne nadchádzajúce udalosti."
                }
            ]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=4)

        print("✓ Kalendár úspešne stiahnutý pomocou priamych tried z HTML!")

    except Exception as e:
        print(f"Chyba pri scrapovaní: {e}")


if __name__ == "__main__":
    get_calendar()
import json
import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def ziskaj_dnesny_obed():
    url = "https://msborska.edupage.org/menu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "menu.json")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extrahujeme všetok čistý text zo stránky a rozbijeme ho na riadky
        lines = soup.get_text(separator="\n", strip=True).split("\n")
        
        weekly_menu = {}
        current_day = None
        current_meal_type = None
        current_meal_desc = []
        
        # Zoznam typov jedál a regex na detekciu dňa (napr. "Po18. 05.", "Ut", "Pondelok")
        meal_types = ["Desiata", "Obed", "Olovrant", "Mliečna desiata"]
        days_regex = r'^(Po|Ut|St|Št|Pi|Pondelok|Utorok|Streda|Štvrtok|Piatok)(\s|$|\d|\.)'
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 1. Je tento riadok názov dňa?
            if re.match(days_regex, line, re.IGNORECASE) and len(line) < 25:
                # Ak už máme nejaké jedlo načítané, najprv ho uložíme
                if current_day and current_meal_type and current_meal_desc:
                    weekly_menu.setdefault(current_day, []).append({
                        "typ": current_meal_type,
                        "nazov": " ".join(current_meal_desc)
                    })
                current_day = line
                current_meal_type = None
                current_meal_desc = []
                continue
                
            # 2. Je to typ jedla? (Desiata, Obed...)
            if current_day:
                is_meal = False
                for mt in meal_types:
                    if line.lower().startswith(mt.lower()):
                        # Uložíme predošlé jedlo
                        if current_meal_type and current_meal_desc:
                            weekly_menu.setdefault(current_day, []).append({
                                "typ": current_meal_type,
                                "nazov": " ".join(current_meal_desc)
                            })
                        
                        # Nastavíme nový typ jedla
                        parts = line.split(":", 1)
                        if len(parts) > 1 and parts[1].strip():
                            current_meal_type = parts[0].strip()
                            current_meal_desc = [parts[1].strip()]
                        else:
                            current_meal_type = line.replace(":", "").strip()
                            current_meal_desc = []
                        is_meal = True
                        break
                
                if is_meal: continue
                
                # 3. Ak to nie je deň ani typ jedla, je to s najväčšou pravdepodobnosťou text samotného jedla
                if current_meal_type:
                    # Odstrihneme zbytočnosti na spodku stránky Edupage
                    # Odstrihneme zbytočnosti na spodku stránky Edupage
                    if any(x in line for x in ["Alergény", "Odkazy", "Kontakty", "Prihlásenie", "Vytvorené v programe"]):
                        break
                    # Preskočíme riadky, kde sú len čísla alergénov alebo gramáže (napr. "1, 3, 7" alebo "150/200")
                    if re.match(r'^[\d,\s/]+$', line):
                        continue
                    
                    current_meal_desc.append(line)
        
        # Uložíme posledný záznam na konci
        if current_day and current_meal_type and current_meal_desc:
            weekly_menu.setdefault(current_day, []).append({
                "typ": current_meal_type,
                "nazov": " ".join(current_meal_desc)
            })

        # Záchranná brzda
        if not weekly_menu:
            weekly_menu = {"Chyba": [{"typ": "Upozornenie", "nazov": "Skriptu sa nepodarilo vyextrahovať text menu."}]}

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(weekly_menu, f, ensure_ascii=False, indent=4)

        print("✓ Lístok pre malého úspešne vyextrahovaný a uložený!")
        
        # Pre dashboard vrátime len zoznam jedál (názvy) pre aktuálny deň
        dnes_idx = datetime.now().weekday()  # 0=Pondelok, 1=Utorok...
        skratky = {0: "Po", 1: "Ut", 2: "St", 3: "Št", 4: "Pi"}
        hladana_skratka = skratky.get(dnes_idx)

        if weekly_menu and "Chyba" not in weekly_menu:
            if hladana_skratka:
                for kluc in weekly_menu.keys():
                    if kluc.startswith(hladana_skratka):
                        return weekly_menu[kluc]
        return [{"typ": "Info", "nazov": "Menu nie je k dispozícii."}]

    except Exception as e:
        print(f"Chyba pri scrapovaní: {e}")
        return [f"Chyba: {e}"]
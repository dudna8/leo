import json
import os
import requests
from bs4 import BeautifulSoup


def ziskaj_udalosti():
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

        # Edupage štruktúra: Hľadáme kontajnery mesiacov a udalostí
        # Každá udalosť je v bloku s triedou, ktorá obsahuje 'CalendarEvent' alebo 'gcal-v3-event'
        # Prejdeme celú stránku odhora nadol po štruktúre
        current_month = "Neznámy mesiac"

        # Prejdeme všetky elementy na stránke, aby sme zachytili poradie mesiacov a udalostí
        all_elements = soup.find_all(
            ["div", "span", "tr"],
            class_=[
                "gcal-v3-monthheader",
                "gcal-v3-event",
                "CalendarMonthHeader",
                "CalendarEventRow",
            ],
        )

        # Ak nenašlo špecifické triedy, skúsime prejsť klasické riadky tabuľky/zoznamu kalendára
        if not all_elements:
            all_elements = soup.find_all(
                "div", class_=lambda x: x and "calendar" in x.lower()
            )

        for el in soup.find_all(True):
            # 1. Zachytenie mesiaca, ak je to nadpis mesiaca
            if el.name in ["div", "h2", "h3"] and any(
                m in el.text.upper()
                for m in ["MÁJ 2026", "JÚN 2026", "JÚL 2026"]
            ):
                current_month = el.text.strip()
                continue

            # 2. Ak je to samotný riadok/blok udalosti
            # Edupage zvyčajne balí text dňa do špecifických tried, poďme vytiahnuť text priamo z vnútorných elementov
            if el.name == "div" and (
                "gcal-v3-event" in el.get("class", [])
                or "CalendarEvent" in el.get("class", [])
            ):
                # Vytiahneme číslo dňa (býva vľavo, napr. "16")
                day_num_el = el.find(
                    class_=["gcal-v3-daynum", "CalendarDayNumber", "dayNumber"]
                )
                # Vytiahneme skratku dňa (napr. "Ut")
                day_name_el = el.find(
                    class_=["gcal-v3-dayname", "CalendarDayName", "dayName"]
                )
                # Vytiahneme text udalosti
                title_el = el.find(
                    class_=[
                        "gcal-v3-title",
                        "CalendarEventTitle",
                        "eventTitle",
                        "jtext",
                    ]
                )

                if title_el:
                    day_num = (
                        day_num_el.text.strip() if day_num_el else "".strip()
                    )
                    day_name = (
                        day_name_el.text.strip() if day_name_el else "".strip()
                    )
                    title_text = title_el.text.strip()

                    # Ak to nenašlo cez presné pod-triedy, rozoberieme text riadku ručne
                    if not day_num:
                        # Skúsime nájsť prvé divy/span-y vo vnútri
                        spans = el.find_all(["span", "div"], limit=3)
                        if len(spans) >= 2:
                            day_num = spans[0].text.strip()
                            day_name = spans[1].text.strip()

                    # Odfiltrujeme zbytočné systémové texty
                    if title_text in [
                        "Celý deň",
                        "Školský výlet",
                        "Kultúrne podujatie",
                        "Exkurzia",
                        "Školská udalosť",
                    ]:
                        continue

                    full_date = f"{day_num}. {day_name} ({current_month})"

                    # Ochrana pred duplicitami
                    if not any(e["nazov"] == title_text for e in events):
                        # Premenujeme 'datum' na 'cas', aby to sedelo s tvojou šablónou index.html
                        events.append({"cas": full_date, "nazov": title_text})

        # Ak horná doménová štruktúra zlyhala, použijeme záložný textový parser na presné riadky zo screenshotu
        if not events:
            lines = [
                line.strip()
                for line in soup.get_text(separator="\n", strip=True).split(
                    "\n"
                )
                if line.strip()
            ]
            temp_day = ""
            temp_wday = ""
            active_month = "Máj 2026"

            for line in lines:
                if any(
                    m in line.upper() for m in ["MÁJ 2026", "JÚN 2026", "JÚL 2026"]
                ):
                    active_month = line
                    continue
                if line.isdigit() and len(line) <= 2:
                    temp_day = line
                    continue
                if line in ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"] and temp_day:
                    temp_wday = line
                    continue
                if (
                    temp_day
                    and len(line) > 10
                    and not any(
                        x in line
                        for x in [
                            "Celý deň",
                            "Školský",
                            "Kultúrne",
                            "Exkurzia",
                            "Alergény",
                        ]
                    )
                ):
                    events.append(
                        {
                            "cas": f"{temp_day}. {temp_wday} - {active_month}",
                            "nazov": line,
                        }
                    )
                    temp_day = ""
                    temp_wday = ""

        # Ak je na konci zoznam úplne prázdny
        if not events:
            events = [
                {
                    "cas": "Info",
                    "nazov": "Momentálne nie sú v kalendári žiadne nadchádzajúce udalosti.",
                }
            ]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=4)

        print("✓ Kalendár úspešne vyextrahovaný!")

    except Exception as e:
        print(f"Chyba pri scrapovaní kalendára: {e}")


if __name__ == "__main__":
    get_calendar()
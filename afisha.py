import json
import time
import random
from curl_cffi import requests
from bs4 import BeautifulSoup

AFISHA_URL = "https://www.dzerteatr.ru/afisha.html"

def fetch_afisha():
    try:
        # Создаём сессию, имитирующую Chrome
        session = requests.Session(impersonate="chrome")
        
        # Сначала заходим на главную, чтобы получить cookies
        print("Заходим на главную...")
        main_resp = session.get("https://www.dzerteatr.ru/", timeout=20)
        print(f"Статус главной: {main_resp.status_code}")
        time.sleep(random.uniform(1, 2))
        
        # Теперь запрашиваем афишу
        print("Запрашиваем афишу...")
        resp = session.get(
            AFISHA_URL,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": "https://www.dzerteatr.ru/",
                "Upgrade-Insecure-Requests": "1",
            },
            timeout=20
        )
        print(f"Статус афиши: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"Тело ответа (первые 500 символов):\n{resp.text[:500]}")
            return {}
        
        soup = BeautifulSoup(resp.text, "html.parser")
        events = {}
        
        for card in soup.find_all("div", class_="event"):
            title_link = card.find("a", class_="play-link")
            if not title_link:
                title_div = card.find("div", class_="event-title")
                title_link = title_div.find("a") if title_div else None
            if not title_link:
                continue
            
            play_name = title_link.get_text(strip=True).rstrip('.').strip()
            play_url = title_link.get("href", "").strip()
            
            date_div = card.find("div", class_="event-date")
            date_text = date_div.get_text(strip=True) if date_div else None
            
            if not play_name:
                continue
            
            if play_name not in events:
                events[play_name] = {"url": play_url, "dates": []}
            
            if date_text:
                events[play_name]["dates"].append(date_text)
        
        return events
    except Exception as e:
        print(f"Ошибка при загрузке афиши: {e}")
        return {}

def main():
    print("Загрузка афиши с официального сайта...")
    events = fetch_afisha()
    print(f"Найдено спектаклей: {len(events)}")
    
    result = []
    for play_name, info in events.items():
        dates = info["dates"]
        unique_dates = list(dict.fromkeys(dates))
        if unique_dates:
            status = f"Ближайшие спектакли: {', '.join(unique_dates)}"
        else:
            status = "О ДАТАХ БЛИЖАЙШИХ СПЕКТАКЛЕЙ СООБЩИМ ДОПОЛНИТЕЛЬНО"
        
        result.append({
            "play": play_name,
            "url": info["url"],
            "dates": unique_dates,
            "status": status
        })
    
    with open("afisha.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print("Готово! Файл afisha.json создан.")
    for item in result[:5]:
        print(f"  {item['play']} — {item['status']}")

if __name__ == "__main__":
    main()
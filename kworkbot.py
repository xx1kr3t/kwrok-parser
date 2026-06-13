import requests
import time
from collections import deque
import os
from dotenv import load_dotenv

load_dotenv()

URL = "https://kwork.ru/projects"

# ====НАСТРОЙКА ТГ БОТА=====
tg_token = os.getenv("TG_TOKEN")
chat_id = os.getenv("CHAT_ID")
#===========================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://kwork.ru/projects",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

PARAMS = {
    "c" : 41,
}

seen = deque(maxlen=500)


def send_tg(text):
    tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = {
        "chat_id" : chat_id, 
        "text" : text,
        "parse_mode" : "HTML",
        "disable_web_page_preview" : True
    }
    try:
        r = requests.post(tg_url, json=payload)
        r.raise_for_status()
    except Exception as e:
        print("Ошибка отправки в телеграмм:", e)


def get_projects(page=1):
    params = PARAMS.copy()
    params["page"] = page

    r = requests.post(URL, data=params, headers=headers)
    r.raise_for_status()
    
    response_data = r.json()
    return response_data.get("data", {}).get("pagination", {}).get("data", [])


def run():
    print("Парсер запущен")

    first_run = True
    while True:
        try:
            projects = get_projects(page=1)
            
            print(f"[{time.strftime('%H:%M:%S')}] Сделали запрос. Проектов в ответе: {len(projects)}")

            for project in projects:
                projectid = project.get("id")
                if not projectid:
                    continue
                
                if projectid in seen:
                    continue

                seen.append(projectid)

                if first_run:
                    continue

                # БЕЗОПАСНО ДОСТАЕМ ДАННЫЕ (с дефолтными значениями)
                name = project.get("name", "Без названия")
                price = project.get("priceLimit", "По договоренности")
                description = project.get("description", "Описание отсутствует")
                
                # Добавил HTML-теги для красоты в ТГ
                text = f"""
🔥 <b>{name}</b>
💰 <b>Бюджет:</b> {price}₽

📄 <b>Описание:</b>
<i>{description[:200]}...</i>

🔗 <a href="https://kwork.ru/projects/{projectid}">Открыть заказ на Kwork</a>"""

                print(f"Новый заказ: {name}")
                send_tg(text)
                
            if first_run:
                print("База старых проектов заполнена, начинаю активный мониторинг")
                first_run = False
                send_tg("🤖 Проверка связи! Парсер успешно запущен и видит заказы.")

            time.sleep(30)

        except Exception as e:
            print("error:", e)
            time.sleep(30)

if __name__ == "__main__":
    run()
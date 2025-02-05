from flask import Flask, send_file
from multiprocessing import Process, Value
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)

TARGET_URL = "https://web.telegram.org/a/"  # Сайт для відкриття
SCREENSHOT_PATH = "screenshot.png"

# Глобальна змінна для перевірки стану браузера
browser_ready = Value("b", False)

def start_browser(browser_ready):
    """Запускає браузер у headful-режимі з віддаленим доступом."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            args=["--remote-debugging-port=9222"]  # Включає доступ через CDP
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto(TARGET_URL, wait_until="networkidle")

        # Визначаємо реальний розмір вікна
        screen_size = page.evaluate("({ width: window.innerWidth, height: window.innerHeight })")
        width = screen_size["width"]
        height = screen_size["height"]
        page.set_viewport_size({"width": width, "height": height})

        print(f"Браузер відкрив {TARGET_URL} ({width}x{height}) та готовий до скріншотів")

        # Позначаємо, що браузер готовий
        browser_ready.value = True

        while True:
            time.sleep(1)  # Тримаємо браузер відкритим

@app.route("/")
def take_screenshot():
    try:
        if not browser_ready.value:
            return "Помилка: Браузер ще не відкрив сторінку", 500

        with sync_playwright() as p:
            # Підключаємось до відкритого браузера
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]  # Отримуємо першу відкриту сторінку

            # Визначаємо поточний розмір вікна перед скріншотом
            screen_size = page.evaluate("({ width: window.innerWidth, height: window.innerHeight })")
            width = screen_size["width"]
            height = screen_size["height"]

            print(f"Робимо скріншот з розміром: {width}x{height}")

            time.sleep(10)  # Чекаємо 10 секунд перед скріншотом

            # Робимо скріншот, що точно відповідає розміру вікна
            page.screenshot(path=SCREENSHOT_PATH, clip={"x": 0, "y": 0, "width": width, "height": height})
            print(f"Скріншот збережено: {SCREENSHOT_PATH}")

            return send_file(SCREENSHOT_PATH, mimetype="image/png")

    except Exception as e:
        return f"Помилка: {str(e)}", 500

if __name__ == "__main__":
    # Запускаємо браузер у окремому процесі
    browser_process = Process(target=start_browser, args=(browser_ready,))
    browser_process.start()

    # Запускаємо Flask-сервер
    app.run(host="0.0.0.0", port=5000)

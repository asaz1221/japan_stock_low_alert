from flask import Flask, jsonify
import subprocess, threading, time, os

app = Flask(__name__)
STATUS = {"running": False, "last_run": None, "last_result": ""}

def background_check():
    STATUS["running"] = True
    STATUS["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    res = subprocess.run(["python", "check.py"], capture_output=True, text=True)
    STATUS["last_result"] = res.stdout[-1000:]
    STATUS["running"] = False

@app.route("/")
def home():
    return "Japan Stock 1-Year Low Monitor is running."

@app.route("/run", methods=["POST"])
def run_check():
    if STATUS["running"]:
        return jsonify({"ok": False, "msg": "Already running"}), 409
    threading.Thread(target=background_check, daemon=True).start()
    return jsonify({"ok": True, "msg": "Started checking"}), 200

@app.route("/status")
def status():
    return jsonify(STATUS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

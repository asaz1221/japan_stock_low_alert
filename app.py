from flask import Flask, jsonify, request
import subprocess, threading, time, os

app = Flask(__name__)

STATUS = {"running": False, "last_run": None, "last_result": ""}

def background_check():
    STATUS["running"] = True
    STATUS["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        res = subprocess.run(
            ["python", "check.py"],
            capture_output=True,
            text=True,
            timeout=1800  # 最大30分
        )
        STATUS["last_result"] = res.stdout[-2000:]  # 最後の出力だけ保持
    except Exception as e:
        STATUS["last_result"] = f"Error during check: {e}"
    finally:
        STATUS["running"] = False

@app.route("/")
def home():
    return "✅ Japan Stock 1-Year Low Monitor is running."

@app.route("/run", methods=["POST"])
def run_check():
    if STATUS["running"]:
        return jsonify({"ok": False, "msg": "Already running"}), 409
    threading.Thread(target=background_check, daemon=True).start()
    return jsonify({"ok": True, "msg": "Started checking"}), 200

@app.route("/status")
def status():
    return jsonify(STATUS)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return "Invalid payload", 400
    print("📩 Webhook received:", payload)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
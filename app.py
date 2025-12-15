import os
import threading
import time
from flask import Flask, jsonify, request

from check import main as run_check

app = Flask(__name__)

# ===== 状態管理 =====
STATUS = {
    "running": False,
    "last_run": None,
    "last_message": ""
}

status_lock = threading.Lock()

# ===== バックグラウンド処理 =====
def background_check():
    with status_lock:
        STATUS["running"] = True
        STATUS["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        STATUS["last_message"] = "Running..."

    try:
        run_check()
        result_msg = "Completed successfully"
    except Exception as e:
        result_msg = f"Error: {e}"

    with status_lock:
        STATUS["running"] = False
        STATUS["last_message"] = result_msg

# ===== ルーティング =====
@app.route("/")
def home():
    return "✅ Japan Stock 1-Year Low Monitor is running."

@app.route("/run", methods=["POST"])
def run():
    # 🔐 簡易認証
    api_key = request.headers.get("X-API-KEY")
    if api_key != os.getenv("RUN_API_KEY"):
        return jsonify({"ok": False, "msg": "Forbidden"}), 403

    with status_lock:
        if STATUS["running"]:
            return jsonify({"ok": False, "msg": "Already running"}), 409

    thread = threading.Thread(
        target=background_check,
        daemon=True
    )
    thread.start()

    return jsonify({"ok": True, "msg": "Started"}), 200

@app.route("/status")
def status():
    with status_lock:
        return jsonify(STATUS)

# ===== エントリーポイント =====
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )

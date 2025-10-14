import os
import csv
import requests
import sqlite3
from datetime import datetime, timedelta

LINE_NOTIFY_ENDPOINT = "https://notify-api.line.me/api/notify"

def load_tickers_from_csv(path: str):
    tickers = []
    with open(path, "r", encoding="utf-8") as f:
        for row in f:
            t = row.strip()
            if t:
                tickers.append(t)
    return tickers

def send_line_notify(token: str, message: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    try:
        r = requests.post(LINE_NOTIFY_ENDPOINT, headers=headers, data=data, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def ensure_db(path="data/notified.db"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE IF NOT EXISTS notified (ticker TEXT PRIMARY KEY, last_notified TEXT)""")
    conn.commit()
    return conn

def was_recently_notified(conn, ticker, days=7):
    row = conn.execute("SELECT last_notified FROM notified WHERE ticker=?", (ticker,)).fetchone()
    if not row:
        return False
    dt = datetime.fromisoformat(row[0])
    return (datetime.utcnow() - dt) < timedelta(days=days)

def record_notified(conn, ticker):
    conn.execute("REPLACE INTO notified (ticker, last_notified) VALUES (?, ?)", (ticker, datetime.utcnow().isoformat()))
    conn.commit()

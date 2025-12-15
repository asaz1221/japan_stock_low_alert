import os
import pandas as pd
import yfinance as yf
import requests
from dotenv import load_dotenv
from datetime import datetime

# =========================
# 設定
# =========================
BATCH_SIZE = 500  # 1回で処理する銘柄数
NOTIFIED_FILE = "notified.csv"

load_dotenv()
IFTTT_WEBHOOK_URL = os.getenv("IFTTT_WEBHOOK_URL")
BATCH_INDEX = int(os.getenv("BATCH_INDEX", "0"))  # Render側で設定可

# =========================
# 通知
# =========================
def send_ifttt(message: str):
    payload = {"value1": message}
    r = requests.post(IFTTT_WEBHOOK_URL, json=payload, timeout=10)
    if r.status_code == 200:
        print("✅ IFTTT通知送信")
    else:
        print("⚠️ IFTTT通知失敗", r.text)

# =========================
# 通知済み管理
# =========================
def load_notified():
    if not os.path.exists(NOTIFIED_FILE):
        return set()
    return set(pd.read_csv(NOTIFIED_FILE)["symbol"])

def save_notified(symbols):
    pd.DataFrame({"symbol": sorted(symbols)}).to_csv(
        NOTIFIED_FILE, index=False
    )

# =========================
# メイン
# =========================
def main():
    tickers_csv = "data/tickers.csv"
    if not os.path.exists(tickers_csv):
        print("❌ tickers.csv が見つかりません")
        return

    all_tickers = pd.read_csv(tickers_csv)["symbol"].dropna().tolist()
    total = len(all_tickers)

    start = BATCH_INDEX * BATCH_SIZE
    end = start + BATCH_SIZE
    tickers = all_tickers[start:end]

    print(f"📈 全銘柄数: {total}")
    print(f"🔹 処理範囲: {start} - {min(end, total)}")

    notified = load_notified()
    new_hits = []

    for t in tickers:
        try:
            df = yf.download(t, period="1y", progress=False)
            if df.empty or "Low" not in df:
                continue

            lows = df["Low"].dropna()
            if len(lows) < 2:
                continue

            last_low = float(lows.iloc[-1])
            prev_min = float(lows.iloc[:-1].min())

            if last_low <= prev_min and t not in notified:
                new_hits.append(f"{t} 安値 {last_low:.2f}")
                notified.add(t)

        except Exception as e:
            print(f"⚠️ {t}: {e}")

    if new_hits:
        msg = "📢 新安値銘柄\n" + "\n".join(new_hits)
        send_ifttt(msg)
        save_notified(notified)
    else:
        print("📌 新安値銘柄なし")

if __name__ == "__main__":
    main()

import os, sys, time
from datetime import datetime
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from utils import load_tickers_from_csv, send_line_notify, ensure_db, was_recently_notified, record_notified

LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "200"))
COOLDOWN_DAYS = int(os.getenv("NOTIFY_COOLDOWN_DAYS", "7"))
DB_PATH = "data/notified.db"

def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def find_new_lows(tickers, conn):
    new_lows = []
    for batch in tqdm(list(chunked(tickers, BATCH_SIZE)), desc="Checking"):
        try:
            data = yf.download(batch, period="1y", group_by="ticker", progress=False)
        except Exception as e:
            print(f"yfinance error: {e}")
            continue
        for t in batch:
            try:
                df = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                if df.empty:
                    continue
                lows = df["Low"].dropna()
                if len(lows) < 2:
                    continue
                last_low = lows.iloc[-1]
                prev_min = lows.iloc[:-1].min()
                if last_low <= prev_min:
                    if was_recently_notified(conn, t, COOLDOWN_DAYS):
                        continue
                    info = yf.Ticker(t).info
                    name = info.get("shortName", "")
                    new_lows.append(f"{t} {name} 安値={last_low}")
                    record_notified(conn, t)
            except Exception as e:
                print(f"Error {t}: {e}")
    return new_lows

def main():
    tickers_csv = "data/tickers.csv"
    if not os.path.exists(tickers_csv):
        print("data/tickers.csv が見つかりません。まず jpx_fetch.py を実行してください。")
        return
    tickers = load_tickers_from_csv(tickers_csv)
    print(f"{len(tickers)} tickers loaded")
    conn = ensure_db(DB_PATH)
    results = find_new_lows(tickers, conn)
    if not results:
        print("No new lows found.")
        return
    msg = "📉 新安値銘柄:
" + "\n".join(results)
    print(msg)
    if LINE_NOTIFY_TOKEN:
        send_line_notify(LINE_NOTIFY_TOKEN, msg)

if __name__ == "__main__":
    main()

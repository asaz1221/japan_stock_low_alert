import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm
import requests
from dotenv import load_dotenv

# .env を読み込む（UTF-8推奨）
load_dotenv()

IFTTT_WEBHOOK_URL = os.getenv("IFTTT_WEBHOOK_URL")
if not IFTTT_WEBHOOK_URL:
    print("⚠️ .env から IFTTT_WEBHOOK_URL が読み込めません。")
    exit()

def send_ifttt_notification(message):
    """IFTTT Webhook経由で通知"""
    payload = {"value1": message}
    try:
        r = requests.post(IFTTT_WEBHOOK_URL, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ IFTTT通知を送信しました")
        else:
            print(f"⚠️ 通知失敗: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"通知エラー: {e}")

def main():
    tickers_csv = "data/tickers.csv"
    if not os.path.exists(tickers_csv):
        print("⚠️ data/tickers.csv が見つかりません。")
        return

    df_csv = pd.read_csv(tickers_csv, encoding="cp932")
    if "symbol" not in df_csv.columns:
        print("⚠️ CSVに 'symbol' 列がありません。")
        return
    tickers = df_csv["symbol"].dropna().tolist()
    print(f"📈 {len(tickers)} tickers loaded")

    new_lows = []

    for t in tqdm(tickers, desc="Checking"):
        try:
            df_stock = yf.download(t, period="1y", progress=False)
            if df_stock.empty:
                continue

            # Low列の取得
            if "Low" not in df_stock.columns:
                # MultiIndexの場合
                if isinstance(df_stock.columns, pd.MultiIndex):
                    low_cols = [col for col in df_stock.columns if col[0] == "Low"]
                    if low_cols:
                        lows = df_stock[low_cols[0]].dropna()
                    else:
                        print(f"Low列が見つかりません: {t}")
                        continue
                else:
                    print(f"Low列が見つかりません: {t}")
                    continue
            else:
                lows = df_stock["Low"].dropna()

            if len(lows) < 2:
                continue

            last_low = lows.iloc[-1]
            prev_min = lows.iloc[:-1].min()

            if last_low <= prev_min:
                name = yf.Ticker(t).info.get("shortName", "")
                new_lows.append(f"{t} {name} 安値={last_low:.2f}")

        except Exception as e:
            print(f"Error {t}: {e}")

    if not new_lows:
        print("📌 新安値は見つかりませんでした。テスト通知を送ります。")
        new_lows = [f"{t} {yf.Ticker(t).info.get('shortName','')} 安値=TEST" for t in tickers]

    msg = "📢 新安値銘柄:\n" + "\n".join(new_lows)
    print(msg)
    send_ifttt_notification(msg)

if __name__ == "__main__":
    main()

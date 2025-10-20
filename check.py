import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm
import requests

# IFTTT Webhook URL（環境変数で設定）
IFTTT_WEBHOOK_URL = os.getenv("IFTTT_WEBHOOK_URL")

def send_ifttt_notification(message):
    """IFTTT Webhook経由でLINE通知"""
    if not IFTTT_WEBHOOK_URL:
        print("⚠️ IFTTT_WEBHOOK_URL が設定されていません。")
        return
    try:
        payload = {"value1": message}
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
        print("⚠️ data/tickers.csv が見つかりません。まず jpx_fetch.py を実行してください。")
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
                print(f"Error {t}: データ取得失敗")
                continue

            # MultiIndex対応: Low列だけ取り出す
            if isinstance(df_stock.columns, pd.MultiIndex):
                if 'Low' in df_stock.columns.get_level_values(0):
                    df_stock = df_stock['Low']
                    if isinstance(df_stock, pd.DataFrame):
                        df_stock = df_stock.iloc[:, 0]
                else:
                    print(f"Low列が不十分: {t}")
                    continue
            else:
                if 'Low' not in df_stock.columns:
                    print(f"Low列が不十分: {t}")
                    continue
                df_stock = df_stock['Low']

            lows = df_stock.dropna()
            if len(lows) < 2:
                print(f"Low列が不十分: {t}")
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
        # 🔹 テスト通知
        for t in tickers:
            name = yf.Ticker(t).info.get("shortName", "")
            new_lows.append(f"{t} {name} 安値=TEST")
    else:
        print("📢 新安値銘柄:")

    msg = "📢 新安値銘柄:\n" + "\n".join(new_lows)
    print(msg)
    send_ifttt_notification(msg)

if __name__ == "__main__":
    main()

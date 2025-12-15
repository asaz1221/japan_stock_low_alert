import os
import pandas as pd
import yfinance as yf
import requests
from dotenv import load_dotenv

load_dotenv()

IFTTT_WEBHOOK_URL = os.getenv("IFTTT_WEBHOOK_URL")
if not IFTTT_WEBHOOK_URL:
    raise RuntimeError("IFTTT_WEBHOOK_URL が設定されていません")

TICKERS_CSV = "data/tickers.csv"

def send_ifttt(message: str):
    payload = {"value1": message}
    r = requests.post(IFTTT_WEBHOOK_URL, json=payload, timeout=10)
    r.raise_for_status()
    print("✅ IFTTT通知を送信しました")

def main():
    if not os.path.exists(TICKERS_CSV):
        print("❌ tickers.csv が見つかりません")
        return

    df_tickers = pd.read_csv(TICKERS_CSV)
    print(f"📈 対象銘柄数: {len(df_tickers)}")

    new_lows = []

    for _, row in df_tickers.iterrows():
        symbol = row["symbol"]
        code = row["code"]
        name = row["name"]

        try:
            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=False
            )

            if df.empty or "Low" not in df.columns:
                continue

            lows = df["Low"].dropna()
            if len(lows) < 2:
                continue

            last_low = float(lows.iloc[-1])
            prev_min = float(lows.iloc[:-1].min())

            # ⭐ 1年新安値判定
            if last_low <= prev_min:
                new_lows.append(
                    f"{code} {name} 安値={last_low:.2f}"
                )

        except Exception as e:
            print(f"⚠️ {symbol} エラー: {e}")

    if not new_lows:
        print("📌 新安値銘柄なし")
        return

    msg = "📢 1年新安値銘柄\n" + "\n".join(new_lows)
    print(msg)
    send_ifttt(msg)

if __name__ == "__main__":
    main()

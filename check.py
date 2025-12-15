import pandas as pd
import yfinance as yf
import requests
import os
import time

# =========================
# 設定
# =========================
TICKERS_CSV = "data/tickers.csv"
IFTTT_URL = os.environ.get("IFTTT_WEBHOOK_URL")  # Renderの環境変数
SLEEP_SEC = 0.1  # 連続アクセス防止

# =========================
# 1銘柄チェック
# =========================
def check_one(symbol, code, name):
    try:
        df = yf.download(
            symbol,
            period="1y",
            progress=False,
            auto_adjust=True
        )
    except Exception:
        return None

    if df.empty or "Low" not in df.columns:
        return None

    lows = df["Low"].dropna()

    # 取引日が1年分ない銘柄は除外
    if len(lows) < 252:
        return None

    # 今日の安値
    today_low = float(lows.iloc[-1])

    # 過去1年（今日を除く）の最安値
    past_year_low = float(lows.iloc[-252:-1].min())

    # 過去1年最安値を更新したら通知対象
    if today_low < past_year_low:
        return {
            "code": code,
            "name": name,
            "today_low": today_low,
            "past_year_low": past_year_low
        }

    return None

# =========================
# メイン処理
# =========================
def main():
    tickers = pd.read_csv(TICKERS_CSV)
    print(f"📈 対象銘柄数: {len(tickers)}")

    results = []

    for _, row in tickers.iterrows():
        symbol = row["symbol"]
        code = row["code"]
        name = row["name"]

        r = check_one(symbol, code, name)
        if r:
            results.append(r)

        time.sleep(SLEEP_SEC)

    if not results:
        print("✅ 過去1年最安値更新銘柄なし")
        return

    # =========================
    # 表示
    # =========================
    print("📢 過去1年最安値更新銘柄")
    lines = []

    for r in results:
        line = (
            f"{r['code']} {r['name']} "
            f"安値={r['today_low']:.2f}"
        )
        print(line)

        lines.append(
            "📉 過去1年最安値更新\n"
            f"{r['code']} {r['name']}\n"
            f"本日の安値: {r['today_low']:.2f}円\n"
            f"直近1年最安値: {r['past_year_low']:.2f}円"
        )

    # =========================
    # IFTTT送信
    # =========================
    if IFTTT_URL:
        message = "\n\n".join(lines)
        requests.post(
            IFTTT_URL,
            json={"value1": message}
        )
        print("✅ IFTTT通知を送信しました")
    else:
        print("⚠ IFTTT_WEBHOOK_URL が未設定です")

# =========================
# 実行
# =========================
if __name__ == "__main__":
    main()

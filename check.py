import pandas as pd
import yfinance as yf
import requests
import os

# ========= 設定 =========
TICKERS_CSV = "data/tickers.csv"
NOTIFIED_CSV = "data/notified.csv"
LINE_WEBHOOK_URL = os.environ.get("LINE_WEBHOOK_URL")

# ========= LINE通知 =========
def send_line(message: str):
    if not LINE_WEBHOOK_URL:
        print("⚠️ LINE_WEBHOOK_URL 未設定")
        return

    payload = {"value1": message}
    try:
        r = requests.post(LINE_WEBHOOK_URL, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ LINE通知送信")
        else:
            print(f"⚠️ LINE通知失敗: {r.status_code}")
    except Exception as e:
        print(f"❌ LINE送信エラー: {e}")

# ========= メイン処理 =========
def main():
    # 銘柄CSV読み込み
    df = pd.read_csv(TICKERS_CSV)

    # 通知済みCSV（なければ作成）
    if os.path.exists(NOTIFIED_CSV):
        notified = pd.read_csv(NOTIFIED_CSV)
    else:
        notified = pd.DataFrame(columns=["symbol"])

    notified_set = set(notified["symbol"])

    for _, row in df.iterrows():
        symbol = row["symbol"]
        code = row["code"]
        name = row["name"]

        # すでに通知済みはスキップ
        if symbol in notified_set:
            continue

        try:
            data = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=False
            )

            # データなし対策
            if data.empty or "Low" not in data:
                print(f"⚠️ {code} {name} データなし（スキップ）")
                continue

            lows = data["Low"].dropna()

            # データ不足対策
            if len(lows) < 2:
                print(f"⚠️ {code} {name} データ不足（スキップ）")
                continue

            # 数値取得（FutureWarning回避）
            last_low = float(lows.iloc[-1])
            past_min = float(lows.iloc[:-1].min())

            # 過去1年最安値更新チェック
            if last_low <= past_min:
                message = (
                    f"{code} {name}\n"
                    f"📉 過去1年最安値更新\n"
                    f"安値 = {last_low:.2f}"
                )
                print(message)
                send_line(message)

                # 通知済みに追加
                notified_set.add(symbol)
                notified = pd.concat(
                    [notified, pd.DataFrame([{"symbol": symbol}])],
                    ignore_index=True
                )

        except Exception as e:
            print(f"❌ {code} {name} 取得失敗: {e}")
            continue

    # 通知済み保存
    notified.to_csv(NOTIFIED_CSV, index=False)

# ========= 実行 =========
if __name__ == "__main__":
    main()

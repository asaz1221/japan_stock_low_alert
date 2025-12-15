import os
import pandas as pd
import yfinance as yf
import requests
from dotenv import load_dotenv
from datetime import datetime

# ===== 設定 =====
load_dotenv()

IFTTT_WEBHOOK_URL = os.getenv("IFTTT_WEBHOOK_URL")
TICKERS_CSV = "data/tickers.csv"
NOTIFIED_FILE = "data/notified.csv"   # 通知済み銘柄の永続化

if not IFTTT_WEBHOOK_URL:
    raise RuntimeError("IFTTT_WEBHOOK_URL が設定されていません")

# ===== 通知 =====
def send_ifttt_notification(message: str):
    payload = {"value1": message}
    r = requests.post(IFTTT_WEBHOOK_URL, json=payload, timeout=10)
    r.raise_for_status()

# ===== メインロジック =====
def main():
    if not os.path.exists(TICKERS_CSV):
        print("⚠️ tickers.csv が見つかりません")
        return

    df = pd.read_csv(TICKERS_CSV, encoding="cp932")
    if "symbol" not in df.columns:
        print("⚠️ CSVに symbol 列がありません")
        return

    tickers = df["symbol"].dropna().unique().tolist()
    print(f"📈 対象銘柄数: {len(tickers)}")

    # 通知済み銘柄の読み込み
    notified = set()
    if os.path.exists(NOTIFIED_FILE):
        notified_df = pd.read_csv(NOTIFIED_FILE)
        notified = set(notified_df["symbol"].astype(str))

    new_hits = []

    for t in tickers:
        try:
            df_stock = yf.download(
                t,
                period="1y",
                progress=False,
                auto_adjust=False
            )

            if df_stock.empty:
                continue

            # Low 列取得（MultiIndex 対応）
            if isinstance(df_stock.columns, pd.MultiIndex):
                if ("Low", "") in df_stock.columns:
                    lows = df_stock[("Low", "")].dropna()
                else:
                    continue
            else:
                if "Low" not in df_stock.columns:
                    continue
                lows = df_stock["Low"].dropna()

            if len(lows) < 2:
                continue

            last_low = float(lows.iloc[-1])
            prev_min = float(lows.iloc[:-1].min())

            # 🔴 新安値 & 未通知
            if last_low <= prev_min and t not in notified:
                new_hits.append(f"{t} 1年安値: {last_low:.2f}")
                notified.add(t)

        except Exception as e:
            print(f"⚠️ {t} エラー: {e}")

    # 新安値なし → 何もしない
    if not new_hits:
        print("📌 新安値銘柄なし")
        return

    # 通知済み保存
    os.makedirs(os.path.dirname(NOTIFIED_FILE), exist_ok=True)
    pd.DataFrame({"symbol": sorted(notified)}).to_csv(
        NOTIFIED_FILE, index=False
    )

    # 通知
    msg = (
        "📢 1年安値を更新した銘柄\n"
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        + "\n".join(new_hits)
    )

    print(msg)
    send_ifttt_notification(msg)
    print("✅ 通知送信完了")

# ===== エントリーポイント =====
if __name__ == "__main__":
    main()

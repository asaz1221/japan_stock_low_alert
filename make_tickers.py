import pandas as pd
import requests
from io import BytesIO
import os

JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

OUTPUT_DIR = "data"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "tickers.csv")

def main():
    print("📥 JPX銘柄一覧を取得中...")

    r = requests.get(JPX_URL, timeout=30)
    r.raise_for_status()

    # xls（古いExcel）なので engine 指定
    df = pd.read_excel(BytesIO(r.content), engine="xlrd")

    # 必要な列だけ抽出
    df = df.rename(columns={
        "コード": "code",
        "銘柄名": "name",
        "市場・商品区分": "market"
    })

    df = df[["code", "name", "market"]]

    # 東証のみ（ETF等を除きたい場合はここを調整）
    df = df[df["market"].str.contains("市場", na=False)]

    # yfinance 用シンボル
    df["symbol"] = df["code"].astype(str) + ".T"

    df = df[["symbol", "code", "name"]].drop_duplicates()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"✅ tickers.csv 作成完了: {len(df)} 銘柄")
    print(f"📄 出力先: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

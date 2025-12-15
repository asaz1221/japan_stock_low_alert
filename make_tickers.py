import pandas as pd
import os
import requests
from io import BytesIO

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tickers.csv")

JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

def main():
    print("📥 JPX銘柄一覧を取得中...")

    r = requests.get(JPX_URL, timeout=30)
    r.raise_for_status()

    df = pd.read_excel(BytesIO(r.content))

    # 列名確認
    if "コード" not in df.columns:
        raise RuntimeError("❌ JPXファイルに「コード」列が見つかりません")

    # 数字4桁のコードのみ抽出（ETF等を除外）
    df["コード"] = df["コード"].astype(str)
    df = df[df["コード"].str.match(r"^\d{4}$")]

    # yfinance用シンボル
    df["symbol"] = df["コード"] + ".T"

    out_df = (
        df[["symbol"]]
        .drop_duplicates()
        .sort_values("symbol")
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"✅ tickers.csv 作成完了: {len(out_df)} 銘柄")
    print(f"📄 出力先: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

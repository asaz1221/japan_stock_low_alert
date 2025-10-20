import pandas as pd
import requests
from io import BytesIO
import zipfile
import os
from bs4 import BeautifulSoup

def fetch_jpx_list(output_path="data/tickers.csv"):
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
    html = requests.get(url, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    a_tags = soup.select("a[href*='data_j'][href$='.zip'], a[href*='data_j'][href$='.xls']")
    if not a_tags:
        print("銘柄リストのリンクが見つかりません")
        return
    link = a_tags[0]["href"]
    if not link.startswith("https"):
        link = "https://www.jpx.co.jp" + link

    print(f"Downloading from {link}...")
    r = requests.get(link, timeout=15)
    if r.status_code != 200:
        print(f"HTTPエラー: {r.status_code}")
        return

    os.makedirs("data", exist_ok=True)

    # ZIP or XLS対応
    if link.endswith(".zip"):
        z = zipfile.ZipFile(BytesIO(r.content))
        z.extractall("data/")
        excel_files = [n for n in z.namelist() if n.endswith((".xls", ".xlsx"))]
        if not excel_files:
            print("ZIP内にExcelファイルが見つかりません")
            return
        path = os.path.join("data", excel_files[0])
    else:
        path = "data/data_j.xls"
        with open(path, "wb") as f:
            f.write(r.content)

    df = pd.read_excel(path)
    code_col = next((c for c in df.columns if "コード" in c), None)
    if not code_col:
        print("銘柄コード列が見つかりません")
        return

    df["コード"] = df[code_col].astype(str).str.zfill(4)
    df["symbol"] = df["コード"] + ".T"
    df[["symbol"]].to_csv(output_path, index=False, encoding="cp932")
    print(f"✅ {len(df)}件の銘柄を {output_path} に保存しました")

def create_dummy_tickers():
    tickers = [
        {"symbol": "7203.T", "name": "トヨタ自動車"},
        {"symbol": "6758.T", "name": "ソニーグループ"},
    ]
    pd.DataFrame(tickers).to_csv("data/tickers.csv", index=False, encoding="cp932")
    print("✅ ダミー tickers.csv を生成しました")

if __name__ == "__main__":
    try:
        fetch_jpx_list()
    except Exception as e:
        print(f"⚠️ JPX取得に失敗: {e}")
        create_dummy_tickers()
import pandas as pd
import requests
from io import BytesIO
import zipfile
import os
from bs4 import BeautifulSoup

def fetch_jpx_list(output_path="data/tickers.csv"):
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    link = None
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "data_j" in href and (href.endswith(".zip") or href.endswith(".xls")):
            link = href
            break
    if not link:
        print("JPX銘柄リストURLが見つかりません")
        return
    if not link.startswith("https"):
        link = "https://www.jpx.co.jp" + link
    print(f"Downloading from {link}...")
    r = requests.get(link)
    z = zipfile.ZipFile(BytesIO(r.content))
    z.extractall("data/")
    for name in z.namelist():
        if name.endswith(".xls") or name.endswith(".xlsx"):
            path = os.path.join("data", name)
            df = pd.read_excel(path)
            if "コード" in df.columns:
                df["コード"] = df["コード"].astype(str).str.zfill(4)
                df["ticker"] = df["コード"] + ".T"
                df[["ticker"]].to_csv(output_path, index=False, header=False)
                print(f"Saved {len(df)} tickers to {output_path}")
                return
    print("銘柄コード列が見つかりません")

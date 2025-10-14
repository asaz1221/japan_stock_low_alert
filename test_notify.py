import requests

# ここに自分の LINE Notify トークンを貼り付けてください
token = "RrOmDSAKO90VWp+DBG0svD0CVDwMNzf/3zT2vNAUY/2RUe0ajILiu37WMApD55hROKoKp4eprV24PVodW6nQHNP4QQF9jwZEaf97Ew47uJuJArhK1GNczSKrF8eL2UZmIUUVmZniknY+e8ZE4yOn4AdB04t89/1O/w1cDnyilFU="

headers = {"Authorization": f"Bearer {token}"}
data = {"message": "✅ テスト通知：PythonからLINE Notifyを送信しました！"}

response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

print("ステータスコード:", response.status_code)
print("レスポンス:", response.text)

import requests

# ── 設定 ──
IFTTT_EVENT_NAME = "stock_alert"  # IFTTT で作った Event Name
IFTTT_KEY = "YOUR_IFTTT_KEY"     # IFTTT Webhook のキーに置き換える

# Webhook URL
WEBHOOK_URL = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_KEY}"

# 送信メッセージ
message = "📢 テスト通知: Python から送信されました！"

# POST 送信
try:
    payload = {"value1": message}
    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    if r.status_code == 200:
        print("✅ IFTTT 経由で LINE に通知を送信しました！")
    else:
        print(f"⚠️ 送信失敗: ステータスコード {r.status_code}, 内容: {r.text}")
except Exception as e:
    print(f"⚠️ エラー発生: {e}")

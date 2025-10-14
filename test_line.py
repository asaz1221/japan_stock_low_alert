from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import PushMessageRequest, TextMessage

# あなたのチャネルアクセストークン（Messaging API設定画面で確認）
configuration = Configuration(access_token="RrOmDSAKO90VWp+DBG0svD0CVDwMNzf/3zT2vNAUY/2RUe0ajILiu37WMApD55hROKoKp4eprV24PVodW6nQHNP4QQF9jwZEaf97Ew47uJuJArhK1GNczSKrF8eL2UZmIUUVmZniknY+e8ZE4yOn4AdB04t89/1O/w1cDnyilFU=")

# あなた自身のユーザーID（LINE Developers → Messaging API設定 → あなたのユーザーID）
user_id = "Ub2310a6da5ae0f2732560717a581a7d5"  # ←ここを実際のIDに書き換える

with ApiClient(configuration) as api_client:
    messaging_api = MessagingApi(api_client)
    message = TextMessage(text="テスト通知：Render連携成功！")
    messaging_api.push_message(PushMessageRequest(to=user_id, messages=[message]))

 
import base64
import requests
import json

# Google Cloud Vision APIキーを入力
API_KEY = "{3.Cloud Vision APIの取得方法で取得したAPI}"

# 解析対象の画像ファイルパスまたはURL
image_path = "C:\\Users\\user\\Desktop\\test.png"

# 画像をBase64形式にエンコード
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

# リクエスト用のJSONデータを作成
request_data = {
    "requests": [
        {
            "image": {"content": encoded_image},
            "features": [{"type": "TEXT_DETECTION"}],
        }
    ]
}

# Vision APIのエンドポイントURL
endpoint_url = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

# APIにPOSTリクエストを送信
response = requests.post(endpoint_url, json=request_data)

# レスポンスを取得
if response.status_code == 200:
    response_data = response.json()

    # テキスト検出結果を表示
    try:
        detected_text = response_data["responses"][0]["textAnnotations"][0]["description"]
        print("検出されたテキスト:")
        print(detected_text)
    except (KeyError, IndexError):
        print("テキストが検出されませんでした。")
else:
    print(f"エラーが発生しました。ステータスコード: {response.status_code}")
    print(response.text)


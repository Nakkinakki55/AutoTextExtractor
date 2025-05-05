 
import os
import base64
import requests
import json

# Google Cloud Vision APIキー
VISION_API_KEY = "{3.Cloud Vision APIの取得方法で取得したAPI}"

# ChatGPT APIキー
OPENAI_API_KEY = "{4.ChatGPT APIの取得方法で取得したAPI}"

# 解析対象のディレクトリパス
DIRECTORY_PATH = "C:\\Users\\user\\Desktop\\image"

# Vision APIエンドポイントURL
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}"

# ChatGPT APIエンドポイントURL
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# サポートされる画像ファイル拡張子
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")


def encode_image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def call_vision_api(encoded_image):
    # APIリクエスト用データ
    request_data = {
        "requests": [
            {
                "image": {"content": encoded_image},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }

    # APIリクエストを送信
    response = requests.post(VISION_API_URL, json=request_data)

    # レスポンスの解析
    if response.status_code == 200:  # 成功した場合
        try:
            # テキスト検出結果を取得
            response_data = response.json()
            return response_data["responses"][0]["textAnnotations"][0]["description"]
        except (KeyError, IndexError):
            # 検出結果が空の場合
            return "テキストが検出されませんでした。"
    else:
        # エラー発生時のメッセージ
        return f"エラー: {response.status_code} - {response.text}"


def format_prompt_for_openai(detected_text):
    return f"""# OCRデータの形式判別と変換指示

## OCRデータ
""" + detected_text + """
---
**まず、上記のOCRデータの内容を解析し、以下のどれかの形式に分類してください**:
- **領収書 (Receipt)**
- **請求書 (Invoice)**
- **手書きのメモ (Handwritten Memo)**
- **名刺情報 (Business Card)**
- **契約書 (Contract)**
- **その他 (Other)**

---

### **領収書 (Receipt) の場合**
- OCRデータが領収書に該当する場合、その内容を以下の領収書フォーマットに変換してください。  
```json
{
 "type": "receipt",
 "receipt_id": "R-20241123-001",
 "date": "2024-11-23",
 "issued_by": "ABC商店",
 "received_by": "山田 太郎",
 "amount": {
   "currency": "JPY",
   "value": 1500
 },
 "payment_method": "現金",
 "details": [
   {
     "item_name": "商品A",
     "quantity": 1,
     "price_per_unit": 1000,
     "total_price": 1000
   },
   {
     "item_name": "商品B",
     "quantity": 1,
     "price_per_unit": 500,
     "total_price": 500
   }
 ],
 "remarks": "ご利用ありがとうございました。"
}
\```
- 必要な情報: 日付、発行元、受領者、金額、支払い方法、品目詳細（商品名、数量、単価、金額）、備考
- 不明な部分はNULLにしてください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。
\---

### **請求書 (Invoice) の場合**
- OCRデータが請求書に該当する場合、その内容を以下の請求書フォーマットに変換してください。
\```json
{
  "type": "invoice",
  "invoice_id": "INV-20241123-001",
  "date": "2024-11-23",
  "due_date": "2024-12-15",
  "issued_by": {
    "company_name": "XYZ株式会社",
    "address": "東京都港区1-1-1",
    "contact": "03-1234-5678",
    "email": "info@xyz.co.jp"
  },
  "billed_to": {
    "company_name": "山田商事",
    "address": "大阪府大阪市2-2-2",
    "contact": "06-9876-5432",
    "email": "yamada@business.co.jp"
  },
  "items": [
    {
      "item_name": "サービスA",
      "description": "サービス内容の詳細説明",
      "quantity": 1,
      "price_per_unit": 100000,
      "total_price": 100000
    },
    {
      "item_name": "商品B",
      "description": "商品の説明",
      "quantity": 5,
      "price_per_unit": 20000,
      "total_price": 100000
    }
  ],
  "subtotal": 200000,
  "tax": {
    "rate": 0.1,
    "amount": 20000
  },
  "total": 220000,
  "payment_instructions": "振込先: 三菱UFJ銀行 東京支店 普通口座 1234567"
}
\```
- 必要な情報: 請求書番号、請求日、支払期限、発行者情報（会社名、住所、連絡先、メール）、請求先情報、品目詳細（商品名、説明、数量、単価、金額）、小計、消費税、合計金額、振込先情報
- 不明な部分はNULLにしてください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。
\---

### **手書きメモ (Handwritten Memo) の場合**
OCRデータが手書きメモに該当する場合、その内容を以下の手書きメモフォーマットに変換してください。
\```json
{
  "type": "handwritten_memo",
  "memo_id": "M-20241123-001",
  "date": "2024-11-23",
  "author": "山田 太郎",
  "content": "来週の会議は火曜日の午前10時から。\n場所: 会議室A。\n議題: 新商品開発について。",
  "tags": ["会議", "予定", "重要"],
  "priority": "高",
  "related_documents": ["INV-20241123-001", "R-20241123-001"]
}
\```
- 必要な情報: メモの日時、作成者、内容、タグ、優先度、関連する書類
- 不明な部分はNULLにしてください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。
---

### **名刺情報 (Business Card) の場合**
- OCRデータが名刺情報に該当する場合、その内容を以下の名刺フォーマットに変換してください。
\```json
{
  "type": "business_card",
  "business_card_id": "BC-20241123-001",
  "name": "田中 一郎",
  "job_title": "営業部長",
  "company_name": "株式会社サンプル",
  "address": "東京都渋谷区1-2-3",
  "phone": "+81-3-1234-5678",
  "email": "ichiro.tanaka@sample.co.jp",
  "website": "https://www.sample.co.jp",
  "social_media": {
    "linkedin": "https://www.linkedin.com/in/ichiro-tanaka",
    "twitter": "https://twitter.com/ichiro_tanaka"
  }
}
\```
- 必要な情報: 名前、役職、会社名、住所、電話番号、メールアドレス、ウェブサイト、ソーシャルメディアリンク
- 不明な部分はNULLにしてください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。

### **契約書 (Contract) の場合**
- OCRデータが契約書に該当する場合、その内容を以下の契約書フォーマットに変換してください。
```json
{
  "type": "contract",
  "contract_id": "CON-20241123-001",
  "contract_date": "2024-11-23",
  "parties": [
    {
      "party_name": "株式会社サンプル",
      "role": "甲",
      "address": "東京都渋谷区1-2-3"
    },
    {
      "party_name": "株式会社テスト",
      "role": "乙",
      "address": "大阪府大阪市4-5-6"
    }
  ],
  "terms": [
    {
      "description": "契約期間",
      "details": "2024年12月1日から2025年11月30日まで"
    },
    {
      "description": "支払条件",
      "details": "毎月末に指定の口座に振り込み"
    }
  ],
  "signatures": [
    {
      "party_name": "株式会社サンプル",
      "signatory_name": "山田 太郎",
      "sign_date": "2024-11-23"
    },
    {
      "party_name": "株式会社テスト",
      "signatory_name": "佐藤 花子",
      "sign_date": "2024-11-23"
    }
  ]
}
\```
- 必要な情報: 契約書番号、契約日、契約当事者（甲、乙）、契約内容（契約期間、支払条件）、署名者情報（署名日含む）
- 不明な部分はNULLにしてください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。
\---

### **その他 (Other) の場合**
OCRデータが上記のいずれにも該当しない場合、その内容を「その他」フォーマットに変換してください。
```json
{
  "type": "other",
  "content": "ここにOCRから抽出されたテキスト情報が入ります。"
}
\```
- 不明な部分については、そのままテキスト情報を「content」フィールドに記載してください。
- 出力するのはJSONのみでお願いします。それ以外の文言は出力しないでください。
"""


def call_openai_api(prompt):
    # リクエストボディ
    request_body = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0  # 応答の一貫性を保つため低温度を設定
    }

    # HTTPヘッダー
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # APIリクエストを送信
    response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(request_body))

    # レスポンスの解析
    if response.status_code == 200:  # 成功した場合
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        # エラー発生時のメッセージ
        return f"Error: {response.status_code}\n{response.text}"


def process_images_in_directory(directory_path):
    # ディレクトリ内の全ファイルを走査
    for root, _, files in os.walk(directory_path):
        for file in files:
            # サポートされる拡張子のファイルのみを対象
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                print(f"\n処理中のファイル: {file_path}")

                # 画像をBase64エンコード
                encoded_image = encode_image_to_base64(file_path)

                # OCR処理
                detected_text = call_vision_api(encoded_image)
                print(f"\n検出されたテキスト:\n{detected_text}")

                # ChatGPT API用プロンプトを作成
                prompt = format_prompt_for_openai(detected_text)

                # ChatGPT APIを呼び出し、結果を取得
                formatted_data = call_openai_api(prompt)
                print(f"\n抽出されたデータ:\n{formatted_data}")

                print("-------------------")


if __name__ == "__main__":
    # メイン処理: 指定ディレクトリ内の画像を処理
    process_images_in_directory(DIRECTORY_PATH)


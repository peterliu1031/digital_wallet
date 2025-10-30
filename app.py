from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# AccessToken (記得 .env 內要正確設 ACCESS_TOKEN)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# API base URL
API_BASE_URL = "https://issuer-sandbox.wallet.gov.tw/api/qrcode/data"

@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'content 不可為空'}), 400

        # Schema
        schema = {
            "vcUid": "00000000_testest123",  # 根據你的專案實際填
            "issuanceDate": "20251013",      # 根據你需求帶入
            "expiredDate": "20261013",       # 根據你需求帶入
            "fields": [
                {
                    "ename": "roc_birthday",
                    "content": content
                }
            ]
        }

        # 呼叫API
        headers = {
            'Access-Token': ACCESS_TOKEN,               # ← 必須用 Access-Token
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        api_url = API_BASE_URL                         # ← 不要多加 /api/setVCItemData
        response = requests.post(api_url, headers=headers, json=schema)

        if response.status_code != 200:
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()

        # 保存 transactionId
        transaction_id = result.get('transactionId')
        print(f"Transaction ID (保存用): {transaction_id}")

        return jsonify({
            'success': True,
            'transactionId': transaction_id,
            'qrCode': result.get('qrCode'),  # base64
            'deepLink': result.get('deepLink')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

CORS(app)  # 支援跨域（前端 fetch API 才不會 CORS 錯誤）

# 環境變數
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
VC_UID = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE = os.getenv("EXPIRED_DATE")

# 首頁
@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

# health check（Render 用）
@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    return jsonify({'status': 'OK'}), 200

# API 路由
@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'content 不可為空'}), 400

        schema = {
            "vcUid": VC_UID,
            "issuanceDate": ISSUANCE_DATE,
            "expiredDate": EXPIRED_DATE,
            "fields": [
                {
                    "ename": "roc_birthday",
                    "content": content
                }
            ]
        }

        headers = {
            'Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        api_url = API_BASE_URL
        response = requests.post(api_url, headers=headers, json=schema)

        # ★ 務必允許 2xx 都算成功
        if not str(response.status_code).startswith("2"):
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()
        transaction_id = result.get('transactionId')
        print(f"Transaction ID: {transaction_id}")

        return jsonify({
            'success': True,
            'transactionId': transaction_id,
            'qrCode': result.get('qrCode'),      # base64
            'deepLink': result.get('deepLink')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 部署到雲端用 gunicorn 啟動，不需啟動 app.run()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

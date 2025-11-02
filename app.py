from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
API_BASE_URL  = os.getenv("API_BASE_URL")  # https://issuer-sandbox.wallet.gov.tw/api/qrcode/data
VC_UID        = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE  = os.getenv("EXPIRED_DATE")

# 發行端查詢 Transaction 狀態 endpoint
TRANSACTION_API_BASE = "https://issuer-sandbox.wallet.gov.tw/issuer/api/v1/transaction"

@app.route('/api/poll-transaction', methods=['GET'])
def poll_transaction():
    transaction_id = request.args.get('transactionId')
    if not transaction_id:
        return jsonify({'error': '缺少 transactionId'}), 400
    url = f"{TRANSACTION_API_BASE}/{transaction_id}"
    headers = {
        'Access-Token': ACCESS_TOKEN,
        'accept': 'application/json'
    }
    try:
        resp = requests.get(url, headers=headers)
        # 沙盒正常已回 json，404 會回 {"message":"找不到"}, 失敗等拋例外
        try:
            result = resp.json()
        except Exception:
            return jsonify({'error': 'API response not JSON', 'raw': resp.text}), 500

        # 這邊根據沙盒真實回傳決定欄位
        # 例如官方定義 result["status"], 你也可回傳 detail 方便 debug
        return jsonify({
            'status': result.get('status', ''),  # e.g. 'issued', 'completed', 'expired'
            'detail': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json(force=True)
        student = data.get('student')
        name = data.get('name')
        class_name = data.get('class')

        if not (student and name and class_name):
            return jsonify({'error': '所有欄位皆為必填'}), 400

        schema = {
            "vcUid": VC_UID,
            "issuanceDate": ISSUANCE_DATE,
            "expiredDate": EXPIRED_DATE,
            "fields": [
                {"ename": "student", "content": student},
                {"ename": "name", "content": name},
                {"ename": "class", "content": class_name}
            ]
        }
        headers = {
            'Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

        response = requests.post(API_BASE_URL, headers=headers, json=schema)
        if not str(response.status_code).startswith("2"):
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()
        transaction_id = result.get('transactionId')
        print(f"Transaction ID (保存用): {transaction_id}")

        return jsonify({
            'success': True,
            'qrCode': result.get('qrCode'),
            'deepLink': result.get('deepLink'),
            'transactionId': transaction_id  # 前端需要用這個去輪詢
        })
    except Exception as e:
        print("Exception:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

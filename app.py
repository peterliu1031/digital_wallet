from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
VC_UID = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE = os.getenv("EXPIRED_DATE")

@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json()
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
        # 沙盒API路徑為 https://issuer-sandbox.wallet.gov.tw/api/qrcode/data
        response = requests.post(API_BASE_URL, headers=headers, json=schema)

        if not str(response.status_code).startswith("2"):
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()
        transaction_id = result.get('transactionId')
        return jsonify({
            'success': True,
            'transactionId': transaction_id,
            'qrCode': result.get('qrCode'),
            'deepLink': result.get('deepLink')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

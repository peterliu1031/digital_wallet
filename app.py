from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
API_BASE_URL  = os.getenv("API_BASE_URL")
VC_UID        = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE  = os.getenv("EXPIRED_DATE")

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json(force=True)
        fields = data.get('fields')
        print("fields =", fields)

        print('DEBUG環境:', ACCESS_TOKEN, API_BASE_URL, VC_UID, ISSUANCE_DATE, EXPIRED_DATE)  # <--- 加這行
        # 檢查必填欄位
        if not fields or not isinstance(fields, list) or not all('ename' in f and 'content' in f for f in fields):
            return jsonify({'error': 'fields 格式不正確，必須帶 ename, content'}), 400

        schema = {
            "vcUid": VC_UID,
            "issuanceDate": ISSUANCE_DATE,
            "expiredDate": EXPIRED_DATE,
            "fields": fields
        }
        headers = {
            'Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        print("API url:", API_BASE_URL)
        print("schema:", schema)
        print("headers:", headers)  # <--- 加這行
        response = requests.post(API_BASE_URL, headers=headers, json=schema)
        print("status:", response.status_code, "text:", response.text)

        if not str(response.status_code).startswith("2"):
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()
        return jsonify({
            'success': True,
            'transactionId': result.get('transactionId'),
            'qrCode': result.get('qrCode'),
            'deepLink': result.get('deepLink')
        })
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


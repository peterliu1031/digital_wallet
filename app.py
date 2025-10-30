from flask import send_from_directory

from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# .env 
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
VC_UID = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE = os.getenv("EXPIRED_DATE")

@app.route('/api/generate-vc', methods=['POST'])
def generate_vc():
    try:
        data = request.get_json()
        studentId = data.get('student')
        name = data.get('name')
        className = data.get('class')
        grade = data.get('grade')

        if not (studentId and name and className and grade):
            return jsonify({'error': '所有欄位皆為必填'}), 400

        schema = {
            "vcUid": VC_UID,  
            "issuanceDate": ISSUANCE_DATE,
            "expiredDate": EXPIRED_DATE,
            "fields": [
                {"ename": "student", "content": studentId},
                {"ename": "name", "content": name},
                {"ename": "class", "content": className},
            ]
        }

        # 呼叫API
        headers = {
            'Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        api_url = API_BASE_URL
        response = requests.post(api_url, headers=headers, json=schema)

        if not str(response.status_code).startswith("2"):
            return jsonify({'error': f'API 錯誤: {response.status_code}, {response.text}'}), 500

        result = response.json()
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

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

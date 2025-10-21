from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# AccessToken
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
            "vcUid": "00000000_testest123",
            "issuanceDate": "20251013",
            "expiredDate": "20261013",
            "fields": [
                {
                    "ename": "roc_birthday",
                    "content": content
                }
            ]
        }
        
        # 呼叫API
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        api_url = f"{API_BASE_URL}/api/setVCItemData"  
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
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# AccessToken
ACCESS_TOKEN = "" 

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
            "vcUid": "00000000_testest123",
            "issuanceDate": "20251013",
            "expiredDate": "20261013",
            "fields": [
                {
                    "ename": "roc_birthday",
                    "content": content
                }
            ]
        }
        
        # 呼叫API
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        api_url = f"{API_BASE_URL}/api/setVCItemData"  
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

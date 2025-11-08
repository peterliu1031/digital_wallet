from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import base64
import json

load_dotenv()
app = Flask(__name__)
CORS(app)

ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
API_BASE_URL  = os.getenv("API_BASE_URL")  # https://issuer-sandbox.wallet.gov.tw/api/qrcode/data
VC_UID        = os.getenv("VC_UID")
ISSUANCE_DATE = os.getenv("ISSUANCE_DATE")
EXPIRED_DATE  = os.getenv("EXPIRED_DATE")
CREDENTIAL_QUERY_BASE = "https://issuer-sandbox.wallet.gov.tw/api/credential/nonce"

def decode_jwt_payload(jwt_token):
    try:
        parts = jwt_token.split('.')
        payload = parts[1]
        padded_payload = payload + '=' * (-len(payload) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded_payload.encode())
        data = json.loads(decoded_bytes)
        return data
    except Exception as e:
        print("JWT decode error:", e)
        return {}

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
            'transactionId': transaction_id
        })
    except Exception as e:
        print("Exception:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/poll-transaction', methods=['GET'])
def poll_transaction():
    transaction_id = request.args.get('transactionId')
    if not transaction_id:
        return jsonify({'error': '缺少 transactionId'}), 400
    url = f"{CREDENTIAL_QUERY_BASE}/{transaction_id}"
    headers = {
        'Access-Token': ACCESS_TOKEN,
        'accept': 'application/json'
    }
    try:
        resp = requests.get(url, headers=headers)
        result = resp.json()
        credential = result.get('credential')
        received = False
        cid = None
        # 只有 credential 有值才解析 payload
        if credential:
            parts = credential.split('.')
            payload = parts[1]
            padded = payload + '=' * (-len(payload)%4)
            decoded = json.loads(base64.urlsafe_b64decode(padded.encode()))
            vc = decoded.get('vc', {})
            status = vc.get('credentialStatus', {})
            # 根據 statusListIndex 判斷領取
            if status.get('statusListIndex', "0") != "0":
                received = True
            cid_url = decoded.get('jti', '')
            cid = cid_url.split('/')[-1] if cid_url else None
        return jsonify({
            'received': received,
            'cid': cid,
            'detail': result
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

@app.route('/api/revoke-credential', methods=['PUT'])
def revoke_credential():
    try:
        # 前端送 json: {"cid":"xxx", "action":"revocation"}
        data = request.get_json(force=True)
        cid = data.get('cid')
        action = data.get('action', 'revocation')
        if not cid:
            return jsonify({'error': '缺少cid'}), 400
        if action != "revocation":
            return jsonify({'error': '目前僅支援revocation'}), 400

        url = f"https://issuer-sandbox.wallet.gov.tw/api/credential/{cid}/{action}"
        headers = {
            'Access-Token': ACCESS_TOKEN,
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        resp = requests.put(url, headers=headers)

        if not str(resp.status_code).startswith("2"):
            return jsonify({'error': f'API錯誤: {resp.status_code}: {resp.text}'}), 500

        try:
            return jsonify({'success': True, 'result': resp.json()})
        except:
            return jsonify({'success': True, 'result_raw': resp.text})
    except Exception as e:
        print("Exception:", e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

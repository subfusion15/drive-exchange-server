@app.route('/')
def home():
    return '✅ Drive Exchange Flask Server is running successfully!'

# Flask server: exchange serverAuthCode for OAuth tokens and ensure a 'Tax Receipts' folder exists on Drive.
# Secure: set CLIENT_ID and CLIENT_SECRET in environment (Render environment variables).
import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'urn:ietf:wg:oauth:2.0:oob')
FOLDER_NAME = os.environ.get('DRIVE_FOLDER_NAME', 'Tax Receipts')

if not CLIENT_ID or not CLIENT_SECRET:
    app.logger.warning('CLIENT_ID or CLIENT_SECRET not set. Set them as environment variables.')

TOKEN_URL = 'https://oauth2.googleapis.com/token'
DRIVE_FILES_URL = 'https://www.googleapis.com/drive/v3/files'

def exchange_code(code):
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    r = requests.post(TOKEN_URL, data=data, headers={'Content-Type':'application/x-www-form-urlencoded'})
    r.raise_for_status()
    return r.json()

def find_or_create_folder(access_token):
    # Search for existing folder
    q = "mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false".format(name=FOLDER_NAME)
    params = {'q': q, 'fields': 'files(id,name)', 'pageSize': 10}
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(DRIVE_FILES_URL, headers=headers, params=params)
    r.raise_for_status()
    items = r.json().get('files', [])
    if items:
        return items[0]['id']
    # create folder
    metadata = {'name': FOLDER_NAME, 'mimeType': 'application/vnd.google-apps.folder'}
    r = requests.post(DRIVE_FILES_URL, headers=headers, json=metadata)
    r.raise_for_status()
    return r.json().get('id')

@app.route('/exchange_code', methods=['POST'])
def exchange_code_route():
    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({'error':'server_misconfigured','message':'CLIENT_ID and CLIENT_SECRET must be set on server env'}), 500
    data = request.get_json() or {}
    code = data.get('code')
    if not code:
        return jsonify({'error':'missing_code'}), 400
    try:
        token_response = exchange_code(code)
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in')
        # ensure folder exists and return its id
        folder_id = None
        if access_token:
            try:
                folder_id = find_or_create_folder(access_token)
            except Exception as e:
                app.logger.error('Folder creation/search failed: %s', e)
                folder_id = None
        return jsonify({'token_response': token_response, 'folder_id': folder_id})
    except requests.HTTPError as e:
        app.logger.error('Token exchange failed: %s', e.response.text if e.response is not None else str(e))
        return jsonify({'error':'exchange_failed','detail': e.response.text if e.response is not None else str(e)}), 500
    except Exception as e:
        app.logger.exception('Unexpected error')
        return jsonify({'error':'server_error','detail': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

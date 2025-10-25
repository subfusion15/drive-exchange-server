Drive Exchange Flask Server (Render)
====================================

This Flask server exposes POST /exchange_code
- Body: { "code": "<serverAuthCode from Android app>" }
- Response: { token_response: { access_token, refresh_token, ... }, folder_id: '<drive folder id>' }

Setup (local):
1. Copy .env.example -> .env and fill CLIENT_ID and CLIENT_SECRET.
2. python -m venv venv
3. source venv/bin/activate   (mac/linux)  or  venv\Scripts\activate (Windows)
4. pip install -r requirements.txt
5. python app.py

Deploy to Render:
- Create a new Web Service on Render, connect to a GitHub repo containing this server folder.
- Set environment variables on Render: CLIENT_ID, CLIENT_SECRET, REDIRECT_URI (optional), DRIVE_FOLDER_NAME (optional).
- Use 'gunicorn app:app' as the start command or leave as default in render.yaml.

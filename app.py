from flask import Flask, redirect, request, jsonify, session, url_for
from flask_cors import CORS
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")
CORS(app)

# Environment variables
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://drive-exchange-server.onrender.com/oauth2callback")
DRIVE_FOLDER_NAME = os.environ.get("DRIVE_FOLDER_NAME", "DriveExchangeUploads")

# OAuth configuration
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

@app.route("/")
def home():
    return jsonify({"status": "✅ Drive Exchange Flask Server is running successfully!"})

@app.route("/auth")
def auth():
    """Start Google OAuth authorization."""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    """Handle OAuth redirect from Google."""
    state = session.get("state")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,

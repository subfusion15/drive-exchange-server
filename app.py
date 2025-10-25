from flask import Flask, redirect, request, jsonify, session, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_fallback_secret")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://drive-exchange-server.onrender.com/oauth2callback")
DRIVE_FOLDER_NAME = os.getenv("DRIVE_FOLDER_NAME", "TaxReceipts")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# --- HOME ROUTE ---
@app.route("/")
def home():
    return jsonify({"message": "Drive Exchange Flask Server is running!"})

# --- AUTHORIZATION ROUTE ---
@app.route("/auth")
def auth():
    flow = Flow.from_client_config(
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
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)

# --- OAUTH CALLBACK ROUTE ---
@app.route("/oauth2callback")
def oauth2callback():
    state = session.get("state")
    if not state:
        return "Missing state parameter", 400

    flow = Flow.from_client_config(
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
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,

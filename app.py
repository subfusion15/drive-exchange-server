from flask import Flask, redirect, request, jsonify
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://drive-exchange-server.onrender.com/oauth2callback")
DRIVE_FOLDER_NAME = os.getenv("DRIVE_FOLDER_NAME", "DriveExchangeUploads")


@app.route("/")
def home():
    return "✅ Drive Exchange Flask Server is running successfully!"


@app.route("/auth")
def auth():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    credentials = flow.credentials

    return jsonify({
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

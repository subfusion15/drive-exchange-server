from flask import Flask, jsonify
import os
from dotenv import load_dotenv

# Load environment variables (Render sets PORT automatically)
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Drive Exchange Flask Server is running successfully!', 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "ok",
        "message": "Server is live and ready."
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

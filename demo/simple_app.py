"""
Simple test Flask app - minimal version for debugging
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Simple home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Policy Navigator - Test</title>
    </head>
    <body>
        <h1>✅ Flask Server is Working!</h1>
        <p>If you can see this page, your Flask server is running correctly.</p>
        <p><a href="/health">Check health endpoint</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running'
    })

if __name__ == '__main__':
    print("="*60)
    print("Simple Test Server")
    print("="*60)
    print("Starting on http://localhost:5000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

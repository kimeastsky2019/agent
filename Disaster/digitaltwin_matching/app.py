from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'digitaltwin_matching'})

@app.route('/api/summary')
def summary():
    """Get service summary"""
    return jsonify({
        'status': 'active',
        'service': 'Digital Twin Matching',
        'description': '스마트 그리드 디지털 트윈 시뮬레이션 및 분석 서비스',
        'version': '1.0.0'
    })

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    if filename == 'dashboard.html':
        return send_from_directory(BASE_DIR, 'dashboard.html')
    return send_from_directory(BASE_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=False)

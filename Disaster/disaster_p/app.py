from flask import Flask, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# HTML 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'disaster-response-complete_1.html')

print(f'BASE_DIR: {BASE_DIR}')
print(f'HTML_FILE: {HTML_FILE}')
print(f'File exists: {os.path.exists(HTML_FILE)}')

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    else:
        return f'HTML file not found: {HTML_FILE}', 404

@app.route('/health')
def health():
    """Health check"""
    return {'status': 'healthy', 'service': 'Disaster Response Platform'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(host='0.0.0.0', port=port, debug=False)

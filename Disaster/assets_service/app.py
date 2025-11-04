from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import json
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Database setup
DB_PATH = 'assets.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            api_url TEXT NOT NULL,
            service_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return redirect('/assets')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'info@gngmeta.com' and password == 'admin1234':
            session['user_id'] = 1
            session['username'] = username
            return redirect('/assets')
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/assets')
@login_required
def assets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM assets ORDER BY created_at DESC')
    assets_list = c.fetchall()
    conn.close()
    
    assets_data = []
    for asset in assets_list:
        assets_data.append({
            'id': asset[0],
            'name': asset[1],
            'type': asset[2],
            'api_url': asset[3],
            'service_url': asset[4],
            'created_at': asset[5]
        })
    
    return render_template('assets.html', assets=assets_data, username=session.get('username'))

@app.route('/api/assets', methods=['GET'])
@login_required
def get_assets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM assets ORDER BY created_at DESC')
    assets_list = c.fetchall()
    conn.close()
    
    assets_data = []
    for asset in assets_list:
        assets_data.append({
            'id': asset[0],
            'name': asset[1],
            'type': asset[2],
            'api_url': asset[3],
            'service_url': asset[4],
            'created_at': asset[5]
        })
    
    return jsonify({'success': True, 'data': assets_data})

@app.route('/api/assets', methods=['POST'])
@login_required
def create_asset():
    try:
        data = request.json
        name = data.get('name')
        asset_type = data.get('type')  # 'demand', 'supply', 'video'
        api_url = data.get('api_url')
        
        if not name or not asset_type or not api_url:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Map type to service URL
        type_to_url = {
            'demand': '/da',
            'supply': '/sa',
            'video': '/ibs'
        }
        
        service_url = type_to_url.get(asset_type, '/')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO assets (name, type, api_url, service_url)
            VALUES (?, ?, ?, ?)
        ''', (name, asset_type, api_url, service_url))
        conn.commit()
        asset_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'id': asset_id,
                'name': name,
                'type': asset_type,
                'api_url': api_url,
                'service_url': service_url
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
@login_required
def delete_asset(asset_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
        conn.commit()
        deleted = c.rowcount > 0
        conn.close()
        
        if deleted:
            return jsonify({'success': True, 'message': 'Asset deleted'})
        else:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5009))
    app.run(host='0.0.0.0', port=port, debug=True)

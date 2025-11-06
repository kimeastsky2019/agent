from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import os
import hashlib
import sqlite3
from functools import wraps

from i18n import (
    available_languages,
    default_language,
    get_js_translations,
    normalize_language,
    translate,
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Database setup
DB_PATH = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create default admin user
    default_password = hashlib.sha256('admin1234'.encode()).hexdigest()
    c.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, email)
        VALUES (?, ?, ?)
    ''', ('info@gngmeta.com', default_password, 'info@gngmeta.com'))
    conn.commit()
    conn.close()

init_db()


def _get_locale():
    lang = session.get("lang")
    if not lang:
        best = request.accept_languages.best_match(list(available_languages().keys()))
        lang = best or default_language()
    lang = normalize_language(lang)
    session["lang"] = lang
    return lang


@app.before_request
def ensure_locale():
    _get_locale()


@app.context_processor
def inject_translations():
    lang = _get_locale()

    def _translate(key, **kwargs):
        return translate(key, lang=lang, **kwargs)

    return {
        "_": _translate,
        "current_lang": lang,
        "supported_languages": available_languages(),
    }

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    _get_locale()
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                SELECT id, username, email FROM users 
                WHERE (username = ? OR email = ?) AND password_hash = ?
            ''', (username, username, password_hash))
            user = c.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                error_message = translate('login_error_invalid_credentials', lang=_get_locale())

    return render_template('login.html', error=error_message)

@app.route('/set_language/<lang>')
def set_language(lang):
    lang_code = normalize_language(lang)
    session['lang'] = lang_code
    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    referrer = request.referrer
    if referrer and referrer.startswith(request.host_url):
        return redirect(referrer)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    lang = session.get('lang')
    session.clear()
    if lang:
        session['lang'] = normalize_language(lang)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    lang = _get_locale()
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        js_translations=get_js_translations(lang),
    )

@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    try:
        data = request.get_json(silent=True) or {}
        scenario_file = data.get('scenario_file', 'sample_transnational_event')
        
        # Import simulation runner
        import sys
        from pathlib import Path
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, base_dir)
        
        from src.energy_network.simulation_runner import SimulationRunner, _default_region_configs
        from src.energy_network.config import OptimizationParameters
        
        # Get absolute path to data directory
        data_root = Path(base_dir) / 'data'
        scenario_path = data_root / f'{scenario_file}.json'
        
        if not scenario_path.exists():
            raise FileNotFoundError(
                translate('error_scenario_missing', lang=_get_locale(), path=scenario_path)
            )
        
        # Run simulation
        runner = SimulationRunner(
            data_root=data_root,
            region_configs=_default_region_configs(),
            optimization_params=OptimizationParameters(),
        )
        result = runner.run(scenario_file)
        
        # Convert result to dict for JSON serialization
        # Handle dispatch_logs - check if it's a dict or object
        dispatches = []
        for d in result.dispatch_logs:
            if isinstance(d, dict):
                dispatches.append(d)
            else:
                # It's an object with attributes
                dispatch_dict = {
                    'region': getattr(d, 'region', ''),
                    'target_region': getattr(d, 'target_region', ''),
                    'energy_mw': getattr(d, 'energy_mw', 0),
                }
                # Handle timestamp
                timestamp = getattr(d, 'timestamp', None)
                if timestamp:
                    if hasattr(timestamp, 'isoformat'):
                        dispatch_dict['timestamp'] = timestamp.isoformat()
                    else:
                        dispatch_dict['timestamp'] = str(timestamp)
                dispatches.append(dispatch_dict)
        
        result_dict = {
            'scenario': result.scenario if hasattr(result, 'scenario') else str(result),
            'dispatches': dispatches
        }
        
        return jsonify({
            'success': True,
            'message': translate('simulation_success', lang=_get_locale()),
            'result': result_dict
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=True)

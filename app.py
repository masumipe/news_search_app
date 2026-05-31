"""
News Search Application - Main Entry Point
This application provides intelligent news search with personalized reading experience
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import NewsSearch, ReportGenerator
from controllers import SearchController, ReportController, SettingsController
from utils.auth import AuthManager
from utils.config import Config
from models import User



# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['DATABASE'] = 'news_search.db'

# Initialize components
login_manager = LoginManager()
login_manager.init_app(app)
auth_manager = AuthManager(app)
config = Config()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(int(user_id))

# Register blueprints for MVC structure
from controllers import search_bp, settings_bp
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(settings_bp, url_prefix='/settings')

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = auth_manager.authenticate(username, password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    """View generated report"""
    report = ReportGenerator.get_report(report_id)
    return render_template('report.html', report=report)

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    """Generate new report"""
    topic = request.form.get('topic')
    region = request.form.get('region')
    
    report = ReportGenerator.generate_report(topic, region)
    return redirect(url_for('view_report', report_id=report.id))

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/ollama/config', methods=['GET', 'POST'])
@login_required
def ollama_config():
    """Configure Ollama API settings"""
    if request.method == 'POST':
        host = request.form.get('host')
        port = request.form.get('port')
        model = request.form.get('model')
        
        # Save configuration
        config.save_ollama_settings(host, port, model)
        return jsonify({'status': 'success'})
    return render_template('ollama_config.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)

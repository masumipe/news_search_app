from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from utils.config import Config
from models import User # Assuming User model is needed for settings

# Create a blueprint for settings
settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.before_request
@login_required
def before_settings_request():
    """Ensure user is logged in before accessing settings."""
    pass

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page handler."""
    config = Config()
    
    if request.method == 'POST':
        # Handle form submission for settings updates
        # Example: Update Ollama settings
        new_host = request.form.get('ollama_host')
        new_port = request.form.get('ollama_port')
        new_model = request.form.get('ollama_model')
        
        if new_host and new_port and new_model:
            config.save_ollama_settings(new_host, new_port, new_model)
            # Add logic to save settings to the database here
            return redirect(url_for('settings_bp.settings', message="Settings updated successfully!"))
        
        # Handle other settings updates...
        return "Error updating settings", 400
    
    # GET request: display settings form
    return render_template('settings.html', config=config)

# You might need to add more routes here, e.g., for profile management
# @settings_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html', user=current_user)
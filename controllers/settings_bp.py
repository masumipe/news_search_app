from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from utils.config import Config
from utils.site_settings import SiteSettings
from models import User # Assuming User model is needed for settings

# Create a blueprint for settings
settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.before_request
@login_required
def before_settings_request():
    """Ensure user is logged in before accessing settings."""
    pass

@settings_bp.route('/', methods=['GET', 'POST'], endpoint='settings', strict_slashes=False)
@login_required
def settings():
    """Settings page handler."""
    config = Config()
    
    if request.method == 'POST':
        # Handle form submission for settings updates
        # Support both old field names (host, port, model) and new field names (ollama_host, etc.)
        new_host = request.form.get('ollama_host') or request.form.get('host')
        new_port = request.form.get('ollama_port') or request.form.get('port')
        new_model = request.form.get('ollama_model') or request.form.get('model')
        
        if new_host and new_port and new_model:
            config.save_ollama_settings(new_host, new_port, new_model)
            # Add logic to save settings to the database here
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings_bp.settings'))
        
        # Handle other settings updates...
        flash('Error: All fields are required.', 'error')
    
    # GET request: display settings form
    return render_template('settings.html', config=config)

@settings_bp.route('/site_settings', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def site_settings():
    """Site settings page handler for managing priority and ignored websites."""
    site_settings_manager = SiteSettings()
    
    if request.method == 'POST':
        # Get form data
        priority_sites_text = request.form.get('priority_sites', '')
        ignored_sites_text = request.form.get('ignored_sites', '')
        
        # Split by newlines and clean up
        priority_sites = [site.strip() for site in priority_sites_text.split('\n') if site.strip()]
        ignored_sites = [site.strip() for site in ignored_sites_text.split('\n') if site.strip()]
        
        # Save settings
        if site_settings_manager.save_settings(priority_sites, ignored_sites):
            flash('Site settings updated successfully!', 'success')
        else:
            flash('Error saving site settings.', 'error')
        
        return redirect(url_for('settings_bp.site_settings'))
    
    # GET request: display site settings form
    priority_sites = site_settings_manager.get_priority_sites()
    ignored_sites = site_settings_manager.get_ignored_sites()
    
    return render_template(
        'site_settings.html',
        priority_sites=priority_sites,
        ignored_sites=ignored_sites
    )

# You might need to add more routes here, e.g., for profile management
# @settings_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html', user=current_user)
import json
import os
from urllib.parse import urlparse


class SiteSettings:
    """Manage site settings for news search priorities and ignored sites."""
    
    def __init__(self):
        self.config_file = 'site_settings.json'
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading site settings: {e}")
                return self._default_settings()
        return self._default_settings()
    
    def _default_settings(self):
        """Return default settings."""
        return {
            'priority_sites': [],
            'ignored_sites': []
        }
    
    def save_settings(self, priority_sites, ignored_sites):
        """Save settings to JSON file."""
        try:
            # Clean up the lists
            priority_sites = [site.strip() for site in priority_sites if site.strip()]
            ignored_sites = [site.strip() for site in ignored_sites if site.strip()]
            
            self.settings = {
                'priority_sites': priority_sites,
                'ignored_sites': ignored_sites
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving site settings: {e}")
            return False
    
    def get_priority_sites(self):
        """Get list of priority sites."""
        return self.settings.get('priority_sites', [])
    
    def get_ignored_sites(self):
        """Get list of ignored sites."""
        return self.settings.get('ignored_sites', [])
    
    def extract_domain(self, url):
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return url
    
    def should_include_article(self, article_url):
        """
        Determine if an article should be included based on site settings.
        
        Rules:
        1. If ignored_sites list is not empty and article URL contains any ignored site, exclude it
        2. If priority_sites list is not empty and article URL contains a priority site, include it
        3. Otherwise, include it by default
        """
        if not article_url:
            return True
        
        article_domain = self.extract_domain(article_url).lower()
        
        # Check if in ignored list
        ignored_sites = self.get_ignored_sites()
        if ignored_sites:
            for ignored_site in ignored_sites:
                if ignored_site.lower() in article_domain:
                    return False
        
        # If priority sites are defined, only include articles from priority sites
        priority_sites = self.get_priority_sites()
        if priority_sites:
            for priority_site in priority_sites:
                if priority_site.lower() in article_domain:
                    return True
            # If priority list exists but article is not from any priority site, exclude it
            return False
        
        # No priority sites defined, include by default (unless ignored)
        return True

import os
import json

class Config:
    def __init__(self):
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'ollama-host')
        self.ollama_port = os.environ.get('OLLAMA_PORT', '11434')
        self.ollama_model = os.environ.get('OLLAMA_MODEL', 'ols-ml-model')
    
    def save_ollama_settings(self, host, port, model):
        """Save Ollama settings to a JSON configuration file."""
        try:
            # Save to JSON file
            config_file = 'ollama_config.json'
            with open(config_file, 'w') as f:
                json.dump({
                    'host': host,
                    'port': port,
                    'model': model
                }, f, indent=4)
            
            # Update instance variables
            self.ollama_host = host
            self.ollama_port = port
            self.ollama_model = model
            
            return True
        except Exception as e:
            print(f"Error saving Ollama settings: {e}")
            return False
    
    def load_ollama_settings(self):
        """Load Ollama settings from a JSON configuration file."""
        try:
            config_file = 'ollama_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.ollama_host = data.get('host', self.ollama_host)
                    self.ollama_port = data.get('port', self.ollama_port)
                    self.ollama_model = data.get('model', self.ollama_model)
                return True
            else:
                print(f"Configuration file {config_file} not found. Using default settings.")
                return False
        except Exception as e:
            print(f"Error loading Ollama settings: {e}")
            return False
    
    def get_ollama_settings(self):
        """Get the current Ollama settings."""
        return {
            'host': self.ollama_host,
            'port': self.ollama_port,
            'model': self.ollama_model
        }

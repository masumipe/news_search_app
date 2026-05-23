import os

class Config:
    def __init__(self):
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'ollama-host')
        self.ollama_port = os.environ.get('OLLAMA_PORT', '11434')
        self.ollama_model = os.environ.get('OLLAMA_MODEL', 'ols-ml-model')
    
    def save_ollama_settings(self, host, port, model):
        self.ollama_host = host
        self.ollama_port = port
        self.ollama_model = model

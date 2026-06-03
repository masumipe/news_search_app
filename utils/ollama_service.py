import requests
import json
from utils.config import Config


class OllamaService:
    """Service for interacting with Ollama API for text summarization."""
    
    def __init__(self):
        self.config = Config()
        self.config.load_ollama_settings()
    
    def get_summary(self, text, max_length=150):
        """Generate a summary of the given text using Ollama."""
        try:
            url = f"http://{self.config.ollama_host}:{self.config.ollama_port}/api/generate"
            
            prompt = f"Summarize the following news headline in {max_length} characters or less:\n\n{text}\n\nSummary:"
            
            payload = {
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                return summary if summary else text[:max_length]
            else:
                # If Ollama fails, return truncated original text
                return text[:max_length]
                
        except Exception as e:
            print(f"Error generating summary with Ollama: {e}")
            # Fallback to truncated original text
            return text[:max_length]
    
    def is_available(self):
        """Check if Ollama service is available."""
        try:
            url = f"http://{self.config.ollama_host}:{self.config.ollama_port}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama service not available: {e}")
            return False

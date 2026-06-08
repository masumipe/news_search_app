"""Standalone launcher for Gradio AI tools interface."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.news_app.app import create_app
from src.news_app.gradio_app.interfaces import create_interfaces

app = create_app("development")

with app.app_context():
    ollama_client = app.ollama_client

demo = create_interfaces(ollama_client)

if __name__ == "__main__":
    print("Starting Gradio interface at http://localhost:7860")
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        share=os.getenv("GRADIO_SHARE", "false").lower() == "true",
    )

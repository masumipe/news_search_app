@"
# News Search Application

## Overview
A web-based application built with Python, Flask, and Gradio (MVC structure) for intelligent news search, personalized reading, and report generation. Integrates with Ollama Local API for advanced analytics.

## Features
- Search news articles by topic and region (priority region supported)
- Personalized reading experience using machine learning (scikit-learn)
- Comprehensive report generation (financial analysis, images, tables, infographics)
- Ollama Local API integration for AI-powered analytics
- User authentication and authorization
- Responsive design for desktop and mobile
- Security best practices

## Directory Structure
news_search_app/
│ app.py
│ requirements.txt
│ README.md
│
├───models/
├───controllers/
├───views/
├───utils/
├───static/
├───templates/
└───reports/

## Setup Instructions

1. **Clone or create the directory structure** (see above).

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   Install dependencies:

Run the application:

Open your browser:
Go to [http://localhost:5000](http://localhost<vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'>:</vscode_annotation>5000)

Default User Credentials
Username: admin
Password: admin123
Settings Menu
Host: Set Ollama Local API host (e.g., localhost)
Port: Set Ollama Local API port (e.g., 11434)
Model: Choose the ML model for Ollama API (e.g., ols-ml-model)
How to Use
Login with your credentials.
Search for news by entering topic and region.
Review the top 10 results (headline, website, summary).
Generate a report for selected results (includes financial analysis, images, tables, infographics).
Adjust settings for Ollama API as needed.
Security
User authentication required for advanced features.
Sensitive data is protected using Flask best practices.
License
MIT License

For any issues, please contact the project maintainer.# news_search_app

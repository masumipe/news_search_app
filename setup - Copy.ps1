# Step 1: Create Directory Structure
mkdir "d:\Others\FinRpt\news_search_app"
mkdir "d:\Others\FinRpt\news_search_app\models"
mkdir "d:\Others\FinRpt\news_search_app\views"
mkdir "d:\Others\FinRpt\news_search_app\controllers"
mkdir "d:\Others\FinRpt\news_search_app\utils"
mkdir "d:\Others\FinRpt\news_search_app\static"
mkdir "d:\Others\FinRpt\news_search_app\templates"
mkdir "d:\Others\FinRpt\news_search_app\reports"

# Step 2: Create requirements.txt
@"
flask==2.3.0
flask-login==0.6.2
gradio==4.15.0
scikit-learn==1.3.0
requests==2.31.0
pandas==2.0.0
matplotlib==3.7.0
seaborn==0.12.0
beautifulsoup4==4.12.0
lxml==4.9.0
python-dotenv==1.0.0
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\requirements.txt" -Encoding utf8

# Step 3: Create models.py
@"
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    @classmethod
    def get_by_id(cls, user_id):
        if user_id == 1:
            return cls(1, 'admin', 'admin123')
        return None

class NewsSearch:
    def __init__(self, id, topic, region, summary, website):
        self.id = id
        self.topic = topic
        self.region = region
        self.summary = summary
        self.website = website

class ReportGenerator:
    def __init__(self, id, topic, region, financial_analysis, images, tables):
        self.id = id
        self.topic = topic
        self.region = region
        self.financial_analysis = financial_analysis
        self.images = images
        self.tables = tables
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\models.py" -Encoding utf8

# Step 4: Create controllers.py
@"
from models import NewsSearch, ReportGenerator

class SearchController:
    @staticmethod
    def search(topic, region, priority_region):
        results = [
            NewsSearch(1, topic, region, f"News about {topic} in {region}", "news1.com"),
            NewsSearch(2, topic, region, f"Breaking news on {topic}", "news2.com"),
            NewsSearch(3, topic, region, f"Analysis of {topic}", "news3.com"),
            NewsSearch(4, topic, region, f"Latest updates on {topic}", "news4.com"),
            NewsSearch(5, topic, region, f"Expert opinion on {topic}", "news5.com"),
            NewsSearch(6, topic, region, f"Market impact of {topic}", "news6.com"),
            NewsSearch(7, topic, region, f"Economic implications of {topic}", "news7.com"),
            NewsSearch(8, topic, region, f"Industry trends in {topic}", "news8.com"),
            NewsSearch(9, topic, region, f"Global perspective on {topic}", "news9.com"),
            NewsSearch(10, topic, region, f"Future outlook for {topic}", "news10.com"),
        ]
        return results

class ReportController:
    @staticmethod
    def generate_report(topic, region):
        report = ReportGenerator(
            id=1,
            topic=topic,
            region=region,
            financial_analysis=f"Financial analysis for {topic} in {region}",
            images=["image1.png", "image2.png"],
            tables=["table1.csv", "table2.csv"]
        )
        return report

class SettingsController:
    @staticmethod
    def get_settings():
        return {
            'host': 'ollama-host',
            'port': '11434',
            'model': 'ols-ml-model'
        }
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\controllers.py" -Encoding utf8

# Step 5: Create utils/auth.py
@"
from flask_login import LoginManager

class AuthManager:
    def __init__(self, app):
        self.app = app
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(self, user_id):
        from models import User
        return User.get_by_id(user_id)
    
    def authenticate(self, username, password):
        if username == 'admin' and password == 'admin123':
            from models import User
            return User(1, 'admin', 'admin123')
        return None
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\utils\auth.py" -Encoding utf8

# Step 6: Create utils/config.py
@"
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
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\utils\config.py" -Encoding utf8

# Step 7: Create templates/index.html
@"
<!DOCTYPE html>
<html>
<head>
    <title>News Search App</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
        button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>News Search Application</h1>
        <p>Welcome to the intelligent news search platform.</p>
        <a href="/search">Search News</a> | 
        <a href="/settings">Settings</a> | 
        <a href="/login">Login</a>
    </div>
</body>
</html>
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\templates\index.html" -Encoding utf8

# Step 8: Create templates/login.html
@"
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
        input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\templates\login.html" -Encoding utf8

# Step 9: Create templates/search.html
@"
<!DOCTYPE html>
<html>
<head>
    <title>Search News</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        input, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search News</h1>
        <form method="POST">
            <input type="text" name="topic" placeholder="Enter search topic" required>
            <input type="text" name="region" placeholder="Region (e.g., US, UK)" required>
            <input type="text" name="priority_region" placeholder="Priority Region" required>
            <button type="submit">Search</button>
        </form>
    </div>
</body>
</html>
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\templates\search.html" -Encoding utf8

# Step 10: Create templates/search_results.html
@"
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .result { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        h2 { color: #333; }
        a { color: #4CAF50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search Results</h1>
        {% for result in results %}
        <div class="result">
            <h2>{{ result.summary }}</h2>
            <p><a href="{{ result.website }}">{{ result.website }}</a></p>
        </div>
        {% endfor %}
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\templates\search_results.html" -Encoding utf8

# Step 11: Create templates/settings.html
@"
<!DOCTYPE html>
<html>
<head>
    <title>Settings</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        input, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Settings</h1>
        <form method="POST">
            <label>Ollama Host:</label>
            <input type="text" name="host" value="ollama-host">
            <label>Ollama Port:</label>
            <input type="text" name="port" value="11434">
            <label>ML Model:</label>
            <input type="text" name="model" value="ols-ml-model">
            <button type="submit">Save Settings</button>
        </form>
    </div>
</body>
</html>
"@ | Out-File -FilePath "d:\Others\FinRpt\news_search_app\templates\settings.html" -Encoding utf8

Write-Host "All files created successfully!"
# NewsAI - Intelligent News Search & AI-Powered Report Generation

A modern, secure web application for intelligent news search, personalized reading, and comprehensive report generation using **Flask**, **Gradio**, **scikit-learn**, and **Ollama Local API**.

## Architecture

```
src/news_app/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── extensions.py          # Flask extensions (SQLAlchemy, Login, CSRF, Migrate)
├── models/                # Database models
│   ├── user.py            # User model (roles: user, analyst, admin)
│   ├── article.py         # Article & ReadingListItem models
│   ├── report.py          # Report & ReportSection models
│   └── preference.py      # UserPreference & UserInteraction models
├── routes/                # Flask blueprints
│   ├── auth.py            # Authentication (login, register, profile)
│   ├── dashboard.py       # Dashboard with recommendations
│   ├── news.py            # News search, article view, reading list
│   ├── reports.py         # Report generation and management
│   └── api.py             # RESTful JSON API endpoints
├── services/              # Business logic layer
│   ├── news_service.py    # News search abstraction (external + local)
│   ├── ollama_client.py   # Ollama LLM client (sentiment, summarization, risks, reports)
│   ├── report_service.py  # Report generation orchestration
│   └── analytics.py       # Analytics aggregation
├── ml/
│   └── recommender.py     # scikit-learn TF-IDF + cosine similarity recommender
├── gradio_app/
│   └── interfaces.py      # Gradio interactive AI tools
├── templates/             # Jinja2 templates (Bootstrap 5 responsive)
└── static/                # CSS, JS assets
```

## Features

### 1. News Search by Topic and Region
- Search by topic keywords with region filtering
- Priority region support — results personalized by user preferences
- Paginated, filterable results with quick actions

### 2. Personalized Reading (scikit-learn)
- TF-IDF vectorization + cosine similarity recommendation
- Tracks user interactions (views, likes, clicks)
- "Recommended for You" section on dashboard with explanation tags

### 3. AI-Powered Report Generation (Ollama)
- Report types: General, Board Summary, Risk Memo, Market Overview, Financial Analysis
- Structured output: executive summary, sector breakdowns, scenario analysis, risk assessment
- Markdown rendering with table and chart support

### 4. Interactive AI Tools (Gradio)
- Ask the AI about an article
- Compare two news stories
- Explain a topic (simple/moderate/expert)
- Sentiment analysis

### 5. Security
- bcrypt password hashing
- Role-based access control (user, analyst, admin)
- CSRF protection (Flask-WTF)
- Input validation, XSS protection
- Secure session cookies

## Quick Start

### Prerequisites
- Python 3.11+
- Ollama (optional, for LLM features)

### Installation

```bash
# Clone and enter directory
cd news-app

# Install dependencies
pip install .

# Or with dev dependencies
pip install ".[dev]"

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings (at minimum set SECRET_KEY)
```

### Run the Application

```bash
# Set environment variable
export FLASK_APP=src.news_app.app:create_app
$env:FLASK_APP = "src.news_app.app:create_app"
export FLASK_ENV=development
$env:FLASK_ENV = development


# Initialize database and seed data
python scripts/seed.py

# Run Flask dev server
flask run --host=0.0.0.0 --port=5000
```

### Run with uv (Recommended)

```bash
uv pip install -e .
uv run flask run
```

### Run Gradio AI Tools (Separate Process)

```bash
python scripts/run_gradio.py
```

### Run with Docker

```bash
docker-compose up --build
```

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `DATABASE_URL` | `sqlite:///news_app.db` | Database connection |
| `NEWS_API_KEY` | `""` | News API key (optional) |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | LLM model name |
| `BCRYPT_ROUNDS` | `12` | Password hashing rounds |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/news/search` | GET | Search news articles |
| `/api/news/article/<id>` | GET | Get article details |
| `/api/analytics/sentiment` | POST | Sentiment analysis |
| `/api/analytics/summarize` | POST | Article summarization |
| `/api/analytics/risks` | POST | Risk extraction |
| `/api/analytics/compare` | POST | Compare two articles |
| `/api/analytics/explain` | POST | Explain a topic |
| `/api/analytics/aggregate` | POST | Aggregate sentiment |
| `/api/report/generate` | POST | Generate a report |
| `/api/report/<id>` | GET | Get report details |
| `/api/user/preferences` | GET/PUT | User preferences |
| `/api/user/interactions` | POST | Record interaction |
| `/api/health` | GET | Health check |

## Testing

```bash
pip install ".[dev]"
pytest tests/ -v
pytest tests/ --cov=src/news_app  # With coverage
```

## Default Users (after seed)

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123!` | Admin |
| `analyst` | `analyst123!` | Analyst |
| `alice` | `password123` | User |
| `bob` | `password123` | User |

## License

MIT

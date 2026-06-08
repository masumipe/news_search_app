import os
from flask import Flask
from dotenv import load_dotenv

from .config import config_map
from .extensions import db, login_manager, csrf, migrate


load_dotenv()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .models import User, Article, Report, ReadingListItem, UserPreference, UserInteraction

        db.create_all()

    from .routes.auth import auth_bp
    from .routes.news import news_bp
    from .routes.reports import reports_bp
    from .routes.dashboard import dashboard_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    csrf.exempt(api_bp)

    from .services.news_service import NewsService
    app.news_service = NewsService(app.config)

    from .services.ollama_client import OllamaClient
    app.ollama_client = OllamaClient(app.config)

    from .ml.recommender import RecommenderService
    app.recommender = RecommenderService()

    @app.context_processor
    def inject_globals():
        return {"app_name": "NewsAI", "current_year": 2026}

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("errors/500.html"), 500

    return app

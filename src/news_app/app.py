import os
import logging
from flask import Flask
from dotenv import load_dotenv

from .config import config_map
from .extensions import db, login_manager, csrf, migrate


load_dotenv()
logger = logging.getLogger(__name__)


def _migrate_schema():
    """Migrate old DB schema (region->country, add news_sources) without data loss."""
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)

    # Migrate articles: rename region -> country
    if "articles" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("articles")}
        if "region" in cols and "country" not in cols:
            logger.info("Migrating articles: renaming region -> country")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE articles RENAME COLUMN region TO country"))
                conn.commit()

    # Migrate reports: rename region -> country
    if "reports" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("reports")}
        if "region" in cols and "country" not in cols:
            logger.info("Migrating reports: renaming region -> country")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE reports RENAME COLUMN region TO country"))
                conn.commit()

    # Migrate user_preferences: rename preferred_regions -> preferred_countries
    if "user_preferences" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("user_preferences")}
        if "preferred_regions" in cols and "preferred_countries" not in cols:
            logger.info("Migrating user_preferences: renaming preferred_regions -> preferred_countries")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user_preferences RENAME COLUMN preferred_regions TO preferred_countries"))
                conn.commit()
        if "news_sources" not in cols:
            logger.info("Migrating user_preferences: adding news_sources column")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user_preferences ADD COLUMN news_sources TEXT DEFAULT '[]'"))
                conn.commit()


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

        _migrate_schema()
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

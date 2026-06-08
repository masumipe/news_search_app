import json
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from ..extensions import db
from ..models.article import Article
from ..models.report import Report
from ..models.preference import UserPreference, UserInteraction
from ..services.report_service import ReportService
from ..services.analytics import AnalyticsService

api_bp = Blueprint("api", __name__)


@api_bp.route("/news/search", methods=["GET"])
@login_required
def search_news():
    topic = request.args.get("q", "")
    country = request.args.get("country", "")
    domains = request.args.get("domains", "")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    language = request.args.get("language", "en")

    service = current_app.news_service

    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    user_countries = pref.get_countries() if pref else []
    news_sources = pref.get_news_sources() if pref else []

    if not domains and news_sources:
        domains = ",".join(service._extract_domains(news_sources))

    results = service.search(
        topic=topic, country=country, domains=domains or None,
        page=page, page_size=page_size,
        date_from=date_from, date_to=date_to, language=language,
        user_countries=user_countries or None,
    )
    return jsonify(results)


@api_bp.route("/news/article/<int:article_id>", methods=["GET"])
@login_required
def get_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    return jsonify(article.to_dict())


@api_bp.route("/news/reading-list", methods=["GET"])
@login_required
def get_reading_list():
    items = (
        Article.query
        .join(Article.reading_list_items)
        .filter_by(user_id=current_user.id)
        .order_by(Article.published_at.desc())
        .all()
    )
    return jsonify([a.to_dict() for a in items])


@api_bp.route("/analytics/sentiment", methods=["POST"])
@login_required
def analyze_sentiment():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400
    result = current_app.ollama_client.analyze_sentiment(text[:2000])
    return jsonify(result)


@api_bp.route("/analytics/summarize", methods=["POST"])
@login_required
def summarize():
    data = request.get_json() or {}
    text = data.get("text", "")
    title = data.get("title", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400
    result = current_app.ollama_client.summarize_article(title, text[:3000])
    return jsonify({"summary": result})


@api_bp.route("/analytics/risks", methods=["POST"])
@login_required
def extract_risks():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400
    result = current_app.ollama_client.extract_risks(text[:3000])
    return jsonify(result)


@api_bp.route("/analytics/compare", methods=["POST"])
@login_required
def compare_articles():
    data = request.get_json() or {}
    article1_id = data.get("article1_id")
    article2_id = data.get("article2_id")
    if not article1_id or not article2_id:
        return jsonify({"error": "Both article1_id and article2_id are required"}), 400
    a1 = db.session.get(Article, article1_id)
    a2 = db.session.get(Article, article2_id)
    if not a1 or not a2:
        return jsonify({"error": "One or both articles not found"}), 404
    result = current_app.ollama_client.compare_articles(a1.to_dict(), a2.to_dict())
    return jsonify(result)


@api_bp.route("/analytics/explain", methods=["POST"])
@login_required
def explain_topic():
    data = request.get_json() or {}
    topic = data.get("topic", "")
    level = data.get("level", "simple")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    result = current_app.ollama_client.explain_topic(topic, level)
    return jsonify({"explanation": result})


@api_bp.route("/analytics/aggregate", methods=["POST"])
@login_required
def aggregate_sentiment():
    data = request.get_json() or {}
    article_ids = data.get("article_ids", [])
    if not article_ids:
        return jsonify({"error": "article_ids are required"}), 400
    articles = []
    for aid in article_ids:
        article = db.session.get(Article, aid)
        if article:
            articles.append(article.to_dict())
    service = AnalyticsService(current_app.ollama_client)
    result = service.aggregate_sentiment(articles)
    return jsonify(result)


@api_bp.route("/report/generate", methods=["POST"])
@login_required
def generate_report():
    data = request.get_json() or {}
    article_ids = data.get("article_ids", [])
    report_type = data.get("report_type", "general")
    title = data.get("title", "")

    if not article_ids:
        return jsonify({"error": "article_ids are required"}), 400

    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    preferences = pref.to_dict() if pref else {}

    service = ReportService(current_app.ollama_client)
    try:
        report = service.generate_report(
            user_id=current_user.id,
            article_ids=article_ids,
            report_type=report_type,
            title=title,
            preferences=preferences,
        )
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/report/<int:report_id>", methods=["GET"])
@login_required
def get_report(report_id):
    report = db.session.get(Report, report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    if report.user_id != current_user.id and not current_user.can("manage_users"):
        return jsonify({"error": "Access denied"}), 403
    return jsonify(report.to_dict())


@api_bp.route("/user/preferences", methods=["GET", "PUT"])
@login_required
def user_preferences():
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
        db.session.commit()

    if request.method == "PUT":
        data = request.get_json() or {}
        if "preferred_topics" in data:
            pref.preferred_topics = ",".join(data["preferred_topics"])
        if "preferred_countries" in data:
            pref.preferred_countries = ",".join(data["preferred_countries"])
        if "news_sources" in data:
            import json
            pref.news_sources = json.dumps(data["news_sources"])
        db.session.commit()
        return jsonify(pref.to_dict())

    return jsonify(pref.to_dict())


@api_bp.route("/user/interactions", methods=["POST"])
@login_required
def record_interaction_api():
    data = request.get_json() or {}
    article_id = data.get("article_id")
    interaction_type = data.get("type")
    value = data.get("value", 1.0)

    if not article_id or not interaction_type:
        return jsonify({"error": "article_id and type are required"}), 400

    from ..models.preference import INTERACTION_TYPES
    if interaction_type not in INTERACTION_TYPES:
        return jsonify({"error": f"Invalid type. Must be one of: {INTERACTION_TYPES}"}), 400

    interaction = UserInteraction(
        user_id=current_user.id,
        article_id=article_id,
        interaction_type=interaction_type,
        value=value,
    )
    db.session.add(interaction)
    db.session.commit()
    return jsonify({"status": "ok"})


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "NewsAI"})

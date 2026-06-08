from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from ..extensions import db
from ..models.article import Article, ReadingListItem
from ..models.preference import UserPreference

news_bp = Blueprint("news", __name__, url_prefix="/news")


@news_bp.route("/search")
@login_required
def search():
    topic = request.args.get("q", "")
    region = request.args.get("region", "global")
    page = request.args.get("page", 1, type=int)

    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    user_regions = pref.get_regions() if pref else []

    service = current_app.news_service
    results = service.search(
        topic=topic,
        region=region,
        page=page,
        prioritize_region=True,
        user_regions=user_regions if user_regions else None,
    )

    if current_app.recommender._fitted and user_regions:
        results["articles"] = current_app.recommender.rank_search_results(
            current_user.id, results["articles"]
        )

    return render_template(
        "news/search.html",
        articles=results["articles"],
        total=results["total_results"],
        page=page,
        query=topic,
        region=region,
        regions=service.REGIONS,
    )


@news_bp.route("/article/<int:article_id>")
@login_required
def view_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        flash("Article not found.", "error")
        return redirect(url_for("news.search"))

    from ..models.preference import UserInteraction

    existing = UserInteraction.query.filter_by(
        user_id=current_user.id,
        article_id=article_id,
        interaction_type="view",
    ).first()
    if not existing:
        interaction = UserInteraction(
            user_id=current_user.id,
            article_id=article_id,
            interaction_type="view",
        )
        db.session.add(interaction)
        db.session.commit()

    in_reading_list = ReadingListItem.query.filter_by(
        user_id=current_user.id,
        article_id=article_id,
    ).first() is not None

    analytics = {}
    try:
        from ..services.analytics import AnalyticsService
        analytics_service = AnalyticsService(current_app.ollama_client)
        analytics = analytics_service.analyze_article(article.to_dict())
    except Exception:
        pass

    return render_template(
        "news/article.html",
        article=article,
        in_reading_list=in_reading_list,
        analytics=analytics,
    )


@news_bp.route("/reading-list")
@login_required
def reading_list():
    items = (
        ReadingListItem.query.filter_by(user_id=current_user.id)
        .order_by(ReadingListItem.added_at.desc())
        .all()
    )
    return render_template("news/reading_list.html", items=items)


@news_bp.route("/reading-list/add/<int:article_id>", methods=["POST"])
@login_required
def add_to_reading_list(article_id):
    service = current_app.news_service
    service.add_to_reading_list(current_user.id, article_id)
    flash("Added to reading list.", "success")
    return redirect(request.referrer or url_for("news.view_article", article_id=article_id))


@news_bp.route("/reading-list/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_reading_list(item_id):
    from ..models.article import ReadingListItem
    item = db.session.get(ReadingListItem, item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash("Removed from reading list.", "info")
    return redirect(request.referrer or url_for("news.reading_list"))


@news_bp.route("/interaction/<int:article_id>", methods=["POST"])
@login_required
def record_interaction(article_id):
    from ..models.preference import UserInteraction

    interaction_type = request.form.get("type", "click")
    if interaction_type not in ("view", "click", "like", "dislike", "share"):
        return jsonify({"error": "Invalid interaction type"}), 400

    interaction = UserInteraction(
        user_id=current_user.id,
        article_id=article_id,
        interaction_type=interaction_type,
    )
    db.session.add(interaction)
    db.session.commit()
    return jsonify({"status": "ok"})

from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

from ..extensions import db
from ..models.article import Article, ReadingListItem
from ..models.report import Report
from ..models.preference import UserPreference

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()

    recent_articles = Article.query.order_by(Article.published_at.desc()).limit(6).all()

    reading_list = (
        ReadingListItem.query.filter_by(user_id=current_user.id)
        .order_by(ReadingListItem.added_at.desc())
        .limit(5)
        .all()
    )

    recent_reports = (
        Report.query.filter_by(user_id=current_user.id)
        .order_by(Report.created_at.desc())
        .limit(5)
        .all()
    )

    recommendations = []
    try:
        recommender = current_app.recommender
        recommendations = recommender.recommend_for_user(
            current_user.id,
            limit=6,
            exclude_ids=[a.id for a in recent_articles],
        )
    except Exception:
        pass

    return render_template(
        "dashboard/index.html",
        recent_articles=recent_articles,
        reading_list=reading_list,
        recent_reports=recent_reports,
        recommendations=recommendations,
        preferences=pref,
    )


@dashboard_bp.route("/recommendations")
@login_required
def recommendations():
    from flask import current_app

    page = request.args.get("page", 1, type=int)
    recommender = current_app.recommender
    results = recommender.recommend_for_user(current_user.id, limit=20)
    return render_template("news/search.html", articles=[r["article"] for r in results], title="Recommended for You")

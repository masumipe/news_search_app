import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from ..extensions import db
from ..models.report import Report
from ..services.report_service import ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def list_reports():
    page = request.args.get("page", 1, type=int)
    service = ReportService(current_app.ollama_client)
    result = service.get_user_reports(current_user.id, page=page)
    return render_template(
        "reports/list.html",
        reports=result["reports"],
        total=result["total"],
        page=result["page"],
    )


@reports_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    from ..models.article import Article

    if request.method == "POST":
        article_ids = request.form.getlist("article_ids")
        report_type = request.form.get("report_type", "general")
        title = request.form.get("title", "")

        if not article_ids:
            flash("Please select at least one article.", "error")
            return redirect(url_for("reports.generate"))

        from ..models.preference import UserPreference
        pref = UserPreference.query.filter_by(user_id=current_user.id).first()
        preferences = pref.to_dict() if pref else {}

        service = ReportService(current_app.ollama_client)
        try:
            report = service.generate_report(
                user_id=current_user.id,
                article_ids=[int(a) for a in article_ids],
                report_type=report_type,
                title=title,
                preferences=preferences,
            )
            flash("Report generated successfully!", "success")
            return redirect(url_for("reports.view_report", report_id=report.id))
        except Exception as e:
            flash(f"Report generation failed: {str(e)}", "error")
            return redirect(url_for("reports.generate"))

    selected_ids = request.args.getlist("article_ids")
    articles = []
    for aid in selected_ids:
        article = db.session.get(Article, int(aid))
        if article:
            articles.append(article)

    return render_template(
        "reports/generate.html",
        articles=articles,
        report_types=Report.REPORT_TYPES,
    )


@reports_bp.route("/<int:report_id>")
@login_required
def view_report(report_id):
    service = ReportService(current_app.ollama_client)
    result = service.get_report(report_id)
    if not result or result["report"].user_id != current_user.id:
        if not current_user.can("manage_users"):
            flash("Report not found.", "error")
            return redirect(url_for("reports.list_reports"))

    return render_template("reports/view.html", **result)


@reports_bp.route("/delete/<int:report_id>", methods=["POST"])
@login_required
def delete_report(report_id):
    service = ReportService(current_app.ollama_client)
    if service.delete_report(report_id, current_user.id):
        flash("Report deleted.", "info")
    else:
        flash("Report not found or access denied.", "error")
    return redirect(url_for("reports.list_reports"))

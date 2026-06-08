from datetime import datetime, timezone
from ..extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    report_type = db.Column(db.String(50), nullable=False, default="general")
    status = db.Column(db.String(20), nullable=False, default="draft")
    content_json = db.Column(db.JSON)
    content_html = db.Column(db.Text)
    summary = db.Column(db.Text)
    article_ids = db.Column(db.String(1000))
    country = db.Column(db.String(100))
    sector = db.Column(db.String(100))
    language = db.Column(db.String(10), default="en")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sections = db.relationship("ReportSection", backref="report", lazy="dynamic", cascade="all, delete-orphan")

    REPORT_TYPES = ("general", "board_summary", "risk_memo", "market_overview", "financial_analysis")
    STATUSES = ("draft", "generating", "completed", "failed")

    def get_article_id_list(self):
        if self.article_ids:
            return [int(x.strip()) for x in self.article_ids.split(",") if x.strip()]
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "report_type": self.report_type,
            "status": self.status,
            "summary": self.summary,
            "country": self.country,
            "sector": self.sector,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReportSection(db.Model):
    __tablename__ = "report_sections"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    section_type = db.Column(db.String(50), default="text")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

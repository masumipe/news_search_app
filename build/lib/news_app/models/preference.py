from datetime import datetime, timezone
from ..extensions import db


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    preferred_topics = db.Column(db.String(500), default="")
    preferred_regions = db.Column(db.String(500), default="")
    preferred_sectors = db.Column(db.String(500), default="")
    preferred_sources = db.Column(db.String(500), default="")
    language = db.Column(db.String(10), default="en")
    dark_mode = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def get_topics(self):
        return [t.strip() for t in self.preferred_topics.split(",") if t.strip()]

    def get_regions(self):
        return [r.strip() for r in self.preferred_regions.split(",") if r.strip()]

    def get_sectors(self):
        return [s.strip() for s in self.preferred_sectors.split(",") if s.strip()]

    def to_dict(self):
        return {
            "preferred_topics": self.get_topics(),
            "preferred_regions": self.get_regions(),
            "preferred_sectors": self.get_sectors(),
            "language": self.language,
            "dark_mode": self.dark_mode,
        }


INTERACTION_TYPES = ("view", "click", "like", "dislike", "share", "save", "time_spent")


class UserInteraction(db.Model):
    __tablename__ = "user_interactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    interaction_type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, default=1.0)
    metadata_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.Index("idx_user_interaction", "user_id", "interaction_type"),
    )

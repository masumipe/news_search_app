from datetime import datetime, timezone
from ..extensions import db


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(100))
    source_name = db.Column(db.String(200))
    author = db.Column(db.String(200))
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(1000), unique=True, nullable=False, index=True)
    url_to_image = db.Column(db.String(1000))
    published_at = db.Column(db.DateTime, index=True)
    content = db.Column(db.Text)
    region = db.Column(db.String(100), index=True)
    language = db.Column(db.String(10), default="en")
    category = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    fetched_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reading_list_items = db.relationship("ReadingListItem", backref="article", lazy="dynamic")
    interactions = db.relationship("UserInteraction", backref="article", lazy="dynamic")

    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(",")]
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "url_to_image": self.url_to_image,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "region": self.region,
            "language": self.language,
            "category": self.category,
            "tags": self.tag_list(),
        }


class ReadingListItem(db.Model):
    __tablename__ = "reading_list"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    notes = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint("user_id", "article_id", name="uq_user_article"),)

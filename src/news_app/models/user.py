from datetime import datetime, timezone
import bcrypt
from flask_login import UserMixin
from ..extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    preferences = db.relationship("UserPreference", backref="user", lazy="dynamic")
    interactions = db.relationship("UserInteraction", backref="user", lazy="dynamic")
    reading_list = db.relationship("ReadingListItem", backref="user", lazy="dynamic")
    reports = db.relationship("Report", backref="author", lazy="dynamic")

    ROLES = ("user", "analyst", "admin")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def has_role(self, role):
        role_index = self.ROLES.index(self.role)
        required_index = self.ROLES.index(role)
        return role_index >= required_index

    def can(self, permission):
        permissions_map = {
            "search": ["user", "analyst", "admin"],
            "read": ["user", "analyst", "admin"],
            "personalize": ["user", "analyst", "admin"],
            "generate_report": ["user", "analyst", "admin"],
            "advanced_analytics": ["analyst", "admin"],
            "export_reports": ["analyst", "admin"],
            "manage_templates": ["analyst", "admin"],
            "manage_users": ["admin"],
            "system_settings": ["admin"],
            "manage_api_keys": ["admin"],
            "view_logs": ["admin"],
        }
        return self.role in permissions_map.get(permission, [])

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

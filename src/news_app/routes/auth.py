from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash("Account is deactivated.", "error")
                return render_template("auth/login.html")
            login_user(user, remember=request.form.get("remember"))
            next_page = request.args.get("next")
            flash("Welcome back!", "success")
            return redirect(next_page or url_for("dashboard.index"))

        flash("Invalid username or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        if len(username) < 3 or len(username) > 80:
            flash("Username must be between 3 and 80 characters.", "error")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("auth/register.html")

        user = User(username=username, email=email, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    from ..models.preference import UserPreference

    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
        db.session.commit()

    if request.method == "POST":
        import json
        pref.preferred_topics = request.form.get("topics", "")
        pref.preferred_countries = request.form.get("countries", "")
        pref.preferred_sectors = request.form.get("sectors", "")
        news_sources_raw = request.form.get("news_sources", "")
        sources_list = [s.strip() for s in news_sources_raw.split("\n") if s.strip()]
        pref.news_sources = json.dumps(sources_list)
        pref.language = request.form.get("language", "en")
        pref.dark_mode = request.form.get("dark_mode") == "on"
        db.session.commit()
        flash("Preferences updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", preferences=pref)

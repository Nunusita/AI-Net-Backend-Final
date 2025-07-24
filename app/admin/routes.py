from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from ..extensions import db
from ..models import User, Clip, Payment
from flask import current_app

admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == current_app.config["ADMIN_EMAIL"] and password == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        return render_template("login.html", error="Credenciales inválidas")
    return render_template("login.html")

@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin.login"))
    users = User.query.count()
    clips = Clip.query.count()
    payments = Payment.query.count()
    return render_template("dashboard.html", users=users, clips=clips, payments=payments)

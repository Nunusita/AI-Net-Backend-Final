from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, PlanType

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"error": "email and password required"}, 400
    if User.query.filter_by(email=email).first():
        return {"error": "email already registered"}, 409
    user = User(email=email, password_hash=generate_password_hash(password), plan=PlanType.FREE)
    db.session.add(user)
    db.session.commit()
    return {"id": user.id, "email": user.email, "plan": user.plan.value}

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "invalid credentials"}, 401
    token = create_access_token(identity=user.id)
    return {"access_token": token}

@auth_bp.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    return {"id": user.id, "email": user.email, "plan": user.plan.value, "expires": user.plan_expires_at.isoformat() if user.plan_expires_at else None, "is_admin": user.is_admin}

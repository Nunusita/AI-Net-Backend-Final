from datetime import datetime, timedelta
from .extensions import db
from sqlalchemy_utils import ChoiceType

class PlanType:
    FREE = "free"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"

PLAN_CHOICES = [
    (PlanType.FREE, "Free"),
    (PlanType.WEEKLY, "Weekly"),
    (PlanType.MONTHLY, "Monthly"),
    (PlanType.YEARLY, "Yearly"),
    (PlanType.LIFETIME, "Lifetime"),
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plan = db.Column(ChoiceType(PLAN_CHOICES), default=PlanType.FREE)
    plan_expires_at = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    clips = db.relationship("Clip", backref="owner", lazy=True)
    payments = db.relationship("Payment", backref="user", lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    stripe_session_id = db.Column(db.String(255))
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(10), default="usd")
    plan = db.Column(ChoiceType(PLAN_CHOICES))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    source_url = db.Column(db.String(1024))
    file_path = db.Column(db.String(1024))
    caption_language = db.Column(db.String(8), default="en")
    style_id = db.Column(db.Integer, db.ForeignKey("style.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Style(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    config = db.Column(db.JSON)

class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date())
    links_processed = db.Column(db.Integer, default=0)
    clips_generated = db.Column(db.Integer, default=0)

def plan_limits(plan):
    if plan == PlanType.FREE:
        return {"weekly_generations": 2, "clips_per_link": 10}
    # Tengo libertad: puedes cambiar estos límites según tus planes pagos
    return {"weekly_generations": 999999, "clips_per_link": 999999}

def plan_expiry(plan):
    now = datetime.utcnow()
    if plan == PlanType.WEEKLY:
        return now + timedelta(weeks=1)
    if plan == PlanType.MONTHLY:
        return now + timedelta(days=30)
    if plan == PlanType.YEARLY:
        return now + timedelta(days=365)
    if plan == PlanType.LIFETIME:
        return None
    return None

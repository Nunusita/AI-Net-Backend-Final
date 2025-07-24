import stripe
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Payment, PlanType, plan_expiry

payments_bp = Blueprint("payments", __name__)

@payments_bp.before_app_request
def init_payments():
    ...
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

PRICES = {
    PlanType.WEEKLY: {"price_id": "price_weekly_xxx", "name": "Weekly"},
    PlanType.MONTHLY: {"price_id": "price_monthly_xxx", "name": "Monthly"},
    PlanType.YEARLY: {"price_id": "price_yearly_xxx", "name": "Yearly"},
    PlanType.LIFETIME: {"price_id": "price_lifetime_xxx", "name": "Lifetime"},
}

@payments_bp.post("/create-checkout-session")
@jwt_required()
def create_checkout_session():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    plan = data.get("plan")
    if plan not in PRICES:
        return {"error": "invalid plan"}, 400

    success_url = data.get("success_url") or "https://yourapp/success?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = data.get("cancel_url") or "https://yourapp/cancel"

    checkout = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        mode="payment",
        line_items=[{"price": PRICES[plan]["price_id"], "quantity": 1}],
        metadata={"user_id": uid, "plan": plan}
    )
    return {"id": checkout.id, "url": checkout.url}

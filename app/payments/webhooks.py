import stripe
from flask import Blueprint, request, current_app
from ..extensions import db
from ..models import User, Payment, PlanType, plan_expiry
from ..notifications.email import send_email

webhooks_bp = Blueprint("webhooks", __name__)

@webhooks_bp.post("/stripe")
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return {"error": str(e)}, 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        plan = session["metadata"]["plan"]
        amount = session["amount_total"]
        currency = session["currency"]
        user = User.query.get(user_id)
        if user:
            pay = Payment(user_id=user.id, stripe_session_id=session["id"], amount=amount, currency=currency, plan=plan)
            user.plan = plan
            user.plan_expires_at = plan_expiry(plan)
            db.session.add(pay)
            db.session.commit()
            # notify
            send_email(to=user.email, subject="Pago recibido", content=f"Tu plan {plan} está activo.")
    return {"ok": True}

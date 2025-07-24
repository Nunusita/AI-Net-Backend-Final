from datetime import datetime, timedelta, date
from ..extensions import db
from ..models import UsageLog, User, PlanType
from flask import current_app

def can_process_link(user: User):
    if user.plan.value != PlanType.FREE:
        return True, None
    # free: 2 times per week
    start_week = (date.today() - timedelta(days=date.today().weekday()))
    used = (UsageLog.query
        .filter(UsageLog.user_id == user.id, UsageLog.date >= start_week)
        .with_entities(db.func.sum(UsageLog.links_processed).label("links"))
        .first())
    used_links = used.links or 0
    limit = current_app.config.get("FREE_WEEKLY_GENERATIONS", 2)
    if used_links >= limit:
        return False, f"Límite semanal alcanzado ({limit})."
    return True, None

def log_usage(user_id, links=0, clips=0):
    today = date.today()
    log = UsageLog.query.filter_by(user_id=user_id, date=today).first()
    if not log:
        log = UsageLog(user_id=user_id, date=today, links_processed=0, clips_generated=0)
        db.session.add(log)
    log.links_processed += links
    log.clips_generated += clips
    db.session.commit()

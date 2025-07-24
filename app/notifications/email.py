import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

def send_email(to, subject, content):
    api_key = current_app.config.get("SENDGRID_API_KEY")
    if not api_key:
        # no-op in dev
        print(f"[DEV EMAIL] to={to} subject={subject}: {content}")
        return
    message = Mail(
        from_email="no-reply@ainet.app",
        to_emails=to,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
    except Exception as e:
        print("sendgrid error", e)

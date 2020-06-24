from .celery import app

from flask import current_app, render_template
from flask_mail import Message

from mail import mail


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise Exception("[MAIL SERVER] not working")

@app.task()
def send_mail(subject, recipients, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    send_async_email(app, msg)

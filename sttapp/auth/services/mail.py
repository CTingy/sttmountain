from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from sttapp.mail import mail


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise Exception("[MAIL SERVER] not working")


def send_mail(subject, sender, recipients, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    thr = Thread(target=send_async_email, args=(app, msg))
    thr.start()
    return thr

from sttapp.app import celery
from flask_mail import Message
from sttapp.exts.mail import mail


@celery.task()
def send_mail(subject, recipients, html_body):

    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    try:
        mail.send(msg)
    except ConnectionRefusedError:
        raise Exception("[MAIL SERVER] not working")

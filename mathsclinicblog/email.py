from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from mathsclinicblog import mail
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MATHSCLINIC_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MATHSCLINIC_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

def send_mail(mail, link, **kwargs):
    sender_mail = "michealakinkuotu6@gmail.com"
    receiver_email = mail
    password = "seunmelody"
    message = MIMEMultipart("alternative")
    message['Subject'] = "Confimation email from MathsClinic Tutors"
    message["From"] = sender_mail
    message["To"] = receiver_email
    text = f"{link}"
    body = MIMEText(text, 'html')
    message.attach(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as server:
        server.login(sender_mail, password)
        server.sendmail(sender_mail, receiver_email, message.as_string())

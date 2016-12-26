from threading import Thread
from flask_mail import Message
from flask import current_app, render_template
from . import mail

def send_asyc_email(app, msg):
    with app.app_context():  # 激活程序上下文环境
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._getcurrent_object()  # werkzeug.local的LocalProxy(LocalStack().top.app)的方法获得
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+''+subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    thr = Thread(target=send_asyc_email, args=[app, msg])
    thr.start()
    return thr
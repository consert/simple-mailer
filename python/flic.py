import os
import os.path
from flask import Flask, abort, request, Response, jsonify
from flask_mail import Mail, Message
import json
from datetime import datetime
import logging
from logging import handlers
from threading import Thread

app = Flask(__name__)

MAIL_FROM = 'user@example.com'
MAIL_NAME = 'User First Name - Last Name'
MAIL_PASS = 'very_secret'
MAIL_SUBJECT = 'Mail Subject'

app.config.update(
    MAIL_SERVER='smtp.example.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=MAIL_FROM,
    MAIL_PASSWORD=MAIL_PASS
)

mail = Mail(app)

file_name = 'message.json'
file_path = os.path.join(app.root_path, file_name)
logs_dir = os.path.join(app.root_path, 'logs')


# decorator
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


@app.route('/', methods=['GET', 'POST'])
def root():
    # create logs dir if needed
    if not os.path.isdir(logs_dir):
        os.mkdir(logs_dir)

    # add an empty json if we do not have a message file
    if not os.path.isfile(file_path):
        with open(file_name, 'w') as f:
            json.dump({}, f)
    # POST Request
    if request.method == 'POST':
        if not request.json:
            return abort(400)
        handler = handlers.RotatingFileHandler(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'logs', 'log.txt'),
                maxBytes=2000000,
                backupCount=50)
        handler.setLevel(logging.INFO)
        app.logger.handlers.clear()
        app.logger.addHandler(handler)
        json_data = request.json
        log_data = json_data.copy()
        log_data['datetime'] = str(datetime.now())
        app.logger.info(log_data)
        # Send mail
        if 'mailto' in json_data:
            send_email(json_data)

        # Save the last message
        with open(file_name, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)

        return jsonify(success=True)

    # GET Request: send last received message
    else:
        last_message = json.load(open(file_path))
        return Response(json.dumps(last_message), mimetype='application/json')


@async
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        mail.send(msg)


def send_email(json_data):
    msg = Message(subject=MAIL_SUBJECT,
                  recipients=[json_data['mailto']],
                  body=json.dumps(json_data, ensure_ascii=False),
                  sender=MAIL_NAME + '<'+MAIL_FROM+'>')
    send_async_email(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

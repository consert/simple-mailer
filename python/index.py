"""
# coding=utf-8
"""
import os.path
import logging.handlers
from datetime import datetime
from threading import Thread

from flask import Flask, abort, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

KEY_MESSAGE = 'message'
KEY_DATETIME = 'datetime'
KEY_LOCATION = 'location'
KEY_LOCATION_UNKNOWN = 'unknown'
KEY_LOCATION_LATITUDE = 'latitude'
KEY_LOCATION_LONGITUDE = 'longitude'
KEY_LOCATION_ADDRESS = 'address'

SMTP_LOGIN = os.getenv('SMTP_LOGIN', 'user@example.com')
SMTP_FROM = os.getenv('SMTP_FROM', 'User First Name - Last Name')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'very_secret')
MAIL_SUBJECT = os.getenv('SMTP_MAIL_SUBJECT', 'Mail Subject')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_SECURE = os.getenv('SMTP_SECURE', '')
app.config.update(
    MAIL_SERVER=SMTP_SERVER,
    MAIL_PORT=SMTP_PORT,
    MAIL_USE_SSL=SMTP_SECURE == 'ssl',
    MAIL_USE_TLS=SMTP_SECURE == 'tls',
    MAIL_USERNAME=SMTP_LOGIN,
    MAIL_PASSWORD=SMTP_PASSWORD
)

mail = Mail(app)

logs_dir = os.path.join(app.root_path, 'logs')
# create logs dir if needed
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

LOG_FILENAME = os.path.join(logs_dir, 'mailer.log')
logger = logging.getLogger("Mailer Logs")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5000000, backupCount=5)
logger.addHandler(handler)


# decorator
def a_sync(f: callable) -> callable:
    """

    :param f: the function to run
    :return: the wrapper of the the new thread
    """
    def wrapper(*args, **kwargs):
        """

        :param args: The function args
        :param kwargs: The function kwargs
        """
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@app.route('/', methods=['GET', 'POST'])
def root():
    """
        The one endpoint
    :return: http response
    """
    if not request.json:
        return abort(400)
    else:
        json_data = request.json
    mailto = request.args.get('mailto', None)
    log_data = json_data.copy()
    log_data['log_datetime'] = str(datetime.now())
    logger.info(log_data)
    # Send mail
    if 'mailto' in json_data:
        mailto = json_data['mailto']
    if mailto is not None:
        send_email(json_data, mailto)
    return jsonify(success=True)


@a_sync
def send_async_email(msg):
    """Background task to send an email with Flask-Mail.
    :param Message msg: object containing the subject, the array of recipients, the body and the sender of the mail
    """
    with app.app_context():
        mail.send(msg)


def get_location_string(location_dict):
    """

    :param location_dict:
    :return:
    """
    if KEY_LOCATION_ADDRESS in location_dict and \
            str(location_dict[KEY_LOCATION_ADDRESS]).lower() != KEY_LOCATION_UNKNOWN:
        return str(location_dict[KEY_LOCATION_ADDRESS])
    if KEY_LOCATION_LATITUDE in location_dict and KEY_LOCATION_LONGITUDE in location_dict \
            and float(location_dict[KEY_LOCATION_LATITUDE]) != 0 and float(location_dict[KEY_LOCATION_LONGITUDE]) != 0:
        return KEY_LOCATION_LATITUDE + ': ' + \
               str(location_dict[KEY_LOCATION_LATITUDE]) + \
               KEY_LOCATION_LONGITUDE + ':' + \
               str(location_dict[KEY_LOCATION_LONGITUDE])
    return None


def get_mail_body(posted_data):
    """

    :param Dict posted_data:
    :return String mail_body: the string in readable format to be used as mail body
    """
    json_data = posted_data
    # Backwards compatibility
    if 'data' in posted_data:
        json_data = posted_data['data']
    mail_body = 'Details: \nDatetime: '
    if KEY_DATETIME in json_data:
        mail_body += str(json_data[KEY_DATETIME])
    else:
        mail_body += str(datetime.now())

    mail_body += ',\nLocation: '
    if KEY_LOCATION in json_data:
        location_string = get_location_string(json_data[KEY_LOCATION])
        mail_body += location_string if location_string is not None and len(location_string) > 1 else 'Unknown'
    else:
        mail_body += 'Unknown'
    mail_body += '\nMessage: '
    if KEY_MESSAGE in json_data:
        mail_body += '"' + json_data[KEY_MESSAGE] + '"'
    return mail_body


def send_email(json_data, to):
    """Prepares a mail Message to be sent as a background task with Flask-Mail

    :param to: list[str] the list of recipients
    :param dict json_data: The dictionary that has info for the mail
    """
    if not isinstance(to, list):
        to = [to]
    msg = Message(subject=MAIL_SUBJECT,
                  recipients=to,
                  body=get_mail_body(json_data),
                  sender=SMTP_LOGIN + '<' + SMTP_FROM + '>')
    send_async_email(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

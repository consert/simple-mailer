import os.path
import logging.handlers
from datetime import datetime
from threading import Thread

from flask import Flask, abort, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

KEY_MESSAGE = 'message'
KEY_DATETIME = 'datetime'
KEY_LOCATION = 'location'
KEY_LOCATION_UNKNOWN = 'unknown'
KEY_LOCATION_LATITUDE = 'latitude'
KEY_LOCATION_LONGITUDE = 'longitude'
KEY_LOCATION_ADDRESS = 'address'

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

logs_dir = os.path.join(app.root_path, 'logs')
# create logs dir if needed
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

LOG_FILENAME = os.path.join(logs_dir, 'flic.log')
logger = logging.getLogger("Flic Logs")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5000000, backupCount=5)
logger.addHandler(handler)


# decorator
def a_sync(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@app.route('/', methods=['POST'])
def root():

    # POST Request
    if not request.json:
        return abort(400)
    json_data = request.json
    log_data = json_data.copy()
    log_data['log_datetime'] = str(datetime.now())
    logger.info(log_data)
    # Send mail
    if 'mailto' in json_data:
        send_email(json_data)
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
    mail_body = 'TRILLION Button Message: \nDatetime: '
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


def send_email(json_data):
    """Prepares a mail Message to be sent as a background task with Flask-Mail

    :param dict json_data: The dictionary that has info for the mail
    """
    msg = Message(subject=MAIL_SUBJECT,
                  recipients=[json_data['mailto']],
                  body=get_mail_body(json_data),
                  sender=MAIL_NAME + '<' + MAIL_FROM + '>')
    send_async_email(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

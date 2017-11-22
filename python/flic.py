import os
import os.path
import json
import yaml
import logging.config
from datetime import datetime
from threading import Thread

from flask import Flask, abort, request, Response, jsonify, send_from_directory
from flask_mail import Mail, Message

logging.config.dictConfig(yaml.load(open('logging.conf')))

app = Flask(__name__)

KEY_ANONYMOUS = 'anonymous'
KEY_USER = 'user'
KEY_DESCRIPTION = 'description'
KEY_EVENT_DATETIME = 'eventDateTime'
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

file_name = 'message.json'
file_path = os.path.join(app.root_path, file_name)
logs_dir = os.path.join(app.root_path, 'logs')


# decorator
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path), 'favicon.ico', mimetype='image/x-icon')


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
        json_data = request.json
        log_data = json_data.copy()
        log_data['log_datetime'] = str(datetime.now())
        log_file = logging.getLogger('file')
        log_file.info(log_data)
        # Send mail
        if 'mailto' in json_data:
            send_email(json_data)

        # Save the last message
        with open(file_name, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False, sort_keys=True, indent=4)

        return jsonify(success=True)

    # GET Request: send last received message
    else:
        last_message = json.load(open(file_path))
        return Response(json.dumps(last_message, ensure_ascii=False, sort_keys=True, indent=4),
                        mimetype='application/json')


@async
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
    if KEY_LOCATION_ADDRESS in location_dict and\
            str(location_dict[KEY_LOCATION_ADDRESS]).lower() != KEY_LOCATION_UNKNOWN:
        return str(location_dict[KEY_LOCATION_ADDRESS])
    if KEY_LOCATION_LATITUDE in location_dict and KEY_LOCATION_LONGITUDE in location_dict:
        if float(location_dict[KEY_LOCATION_LATITUDE]) != 0 and float(location_dict[KEY_LOCATION_LONGITUDE]) != 0:
            return KEY_LOCATION_LATITUDE + ': ' +\
                   str(location_dict[KEY_LOCATION_LATITUDE]) +\
                   KEY_LOCATION_LONGITUDE + ':' +\
                   str(location_dict[KEY_LOCATION_LONGITUDE])
    return None


def get_mail_body(posted_data):
    """

    :param Dict posted_data:
    :return String mail_body: the string in readable format to be used as mail body
    """
    json_data = posted_data
    if 'data' in posted_data:
        json_data = posted_data['data']

    mail_body = ''
    if KEY_ANONYMOUS in json_data and \
            json_data[KEY_ANONYMOUS]:
        mail_body += 'A user with hidden id'
    elif KEY_USER in json_data:
        mail_body += 'The user with the button ' + json_data[KEY_USER] + ', '
    else:
        mail_body += 'An unknown user'

    mail_body += '\nhas sent on '

    if KEY_EVENT_DATETIME in json_data:
        mail_body += str(json_data[KEY_EVENT_DATETIME])
    else:
        mail_body += str(datetime.now())

    mail_body += ',\nfrom '
    if KEY_LOCATION in json_data:
        location_string = get_location_string(json_data[KEY_LOCATION])
        mail_body += 'location: ' + location_string if location_string is not None else 'an unknown location,'

    mail_body += '\nthe message: \n'
    if KEY_DESCRIPTION in json_data:
        mail_body += '"' + json_data[KEY_DESCRIPTION] + '"'

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


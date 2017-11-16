import os
import os.path
from flask import Flask, abort, request, Response, jsonify
from flask_mail import Mail, Message
import json

app = Flask(__name__)

MAIL_FROM = 'user@example.com'
MAIL_NAME = 'User First Name - Last Name'
MAIL_PASS = 'very_secret'
MAIL_SUBJECT = 'Mail Subject'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=MAIL_FROM,
    MAIL_PASSWORD=MAIL_PASS
)

mail = Mail(app)
file_name = 'message.json'
file_path = os.path.join(app.root_path, file_name)


@app.route('/', methods=['GET', 'POST'])
def root():
    # add an empty json if we do not have a file
    if not os.path.isfile(file_path):
        with open(file_name, 'w') as f:
            json.dump({}, f)
    # POST Request
    if request.method == 'POST':
        if not request.json:
            return abort(400)
        json_data = request.json
        # Send mail
        if 'mailto' in json_data:
            msg = Message(subject=MAIL_SUBJECT,
                          recipients=[json_data['mailto']],
                          body=json.dumps(json_data, ensure_ascii=False),
                          sender=MAIL_NAME + '<'+MAIL_FROM+'>')
            try:
                mail.send(msg)
            except BaseException:
                return abort(500)

        # Save the last message
        with open(file_name, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)
        return jsonify(success=True)

    # GET Request: send last received message
    else:
        last_message = json.load(open(file_path))
        return Response(json.dumps(last_message), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

# Simple server apps to send mail
Three examples for logging and sending emails using smtp when receiving a POST request with a "mailto" key. Examples are in php, Node.js and Python (flask).
The apps expect a posted JSON (content-type:application/json) in a format like:

    {
        "mailto": "user@example.com",
        "message": "string",
        "datetime": "string",
        "location": {
            "address": "string",
            "latitude": float,
            "longitude": float
        }
    }
 
The `mailto` key/value pair is optional,
it can also be set as a GET argument (http(s)://your.server.com/prefix?mailto=user@example.com).

Libraries used for mail: 
  
  * php: [phpmailer](https://github.com/PHPMailer/PHPMailer), licence: [LGPL](https://github.com/PHPMailer/PHPMailer/blob/master/LICENSE)
  * Node.js: [nodemailer](https://github.com/nodemailer/nodemailer), licence: [MIT](https://github.com/nodemailer/nodemailer/blob/master/LICENSE)
  * Python: [Flask-Mail](https://github.com/mattupstate/flask-mail), licence: [BSD 3-clause](https://github.com/mattupstate/flask-mail/blob/master/LICENSE)
  ### Instructions:
  create a .env (see: [.env.template](.env.template)) file in the same folder with index.(php/js/py) with:
  ```
  SMTP_SERVER=smtp.eaxmple.com
  SMTP_PORT=587
  SMTP_LOGIN=user@example.com
  SMTP_PASSWORD=_secret_
  SMTP_AUTH=true
  SMTP_SECURE=tls|ssl
  SMTP_FROM='User First Name - Last Name'
  SMTP_MAIL_SUBJECT='Mail Subject'
```
  #### Node.js:
    cd node && yarn # or npm install    
    yarn start # or npm run start

  #### php:
  make sure [composer](https://getcomposer.org/) is installed
  ```
  cd php && composer install
  ```
    
  #### Python3:
  in virtualenv or not:
  
    cd python && pip install -r requirements.txt
  
  start server with
  
    uwsgi --ini mailer.ini
  
    
  ### Example nginx server config parts:
  
    # PHP:
    root /path/to/simple-mailer/php;
    index index.php index.html index.htm;
    location ~ \.php$ {
        fastcgi_pass        unix:///path/to/php-fpm.sock;
        fastcgi_index       index.php;
        include             fastcgi_params;
        fastcgi_param       SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }	
    
    # Python / uwsgi:	
    location / {
        include             uwsgi_params;
        uwsgi_pass          unix:///path/to/simple-mailer/python/uwsgi-mailer.sock;
        uwsgi_ignore_client_abort on;
    }
    
    # NODE JS:
    location / {
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_set_header        X-Forwarded-For $remote_addr;
        proxy_pass              http://localhost:3000/;
        proxy_cache_bypass      $http_upgrade;
        proxy_redirect          off;
    }
  

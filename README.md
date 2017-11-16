# trillion-flic-server

  ### node.js:
    cd node && npm install
  Change mail settings on config.js file:

    mailConfig: {
      host: 'smtp.example.com',
      port: 587,
      secure: false,
      auth: {
        user: 'user@example.com',
        pass: 'very_secret'
      }
    },
    mailerName: 'User First Name - Last Name',
    mailSubject: 'Mail Subject'

  start server with
    
    npm run start

  ### php:
  change mail options on php/config.php:

    define('MAIL_USER','user@example.com');
    define('MAIL_PASSWORD','very_secret');
    define('MAIL_NAME','User First Name - Last Name');
    define('MAIL_SUBJECT','Mail Subject');
    define('SMTP_AUTH',true);
    define('SMTP_SECURE','tls');
    define('SMTP_HOST', 'smtp.example.com');
    define('SMTP_PORT',587);
    
  ### python:
  from virtualenv or not:
  
    cd python && pip install -r requirements.txt
  change mail settings on flic.py:
  
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
  
  start server with
  
    uwsgi --ini flic.ini
  
    
  ### example nginx server config parts:
  
    # PHP:
    root /path/to/trillion-flic-server/php;
    index index.php index.html index.htm;
    location ~ \.php$ {
        fastcgi_pass        unix:/run/php-fpm/php-fpm.sock;
        fastcgi_index       index.php;
        include             fastcgi_params;
        fastcgi_param       SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }	
    
    # Python / uwsgi:	
    location / {
        include             uwsgi_params;
        uwsgi_pass          unix:/path/to/trillion-flic-server/python/flic.sock;
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
  

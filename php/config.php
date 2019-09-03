<?php

define('KEY_MESSAGE', 'message');
define('KEY_DATETIME','datetime');
define('KEY_LOCATION','location');
define('KEY_LOCATION_UNKNOWN','unknown');
define('KEY_LOCATION_LATITUDE','latitude');
define('KEY_LOCATION_LONGITUDE','longitude');
define('KEY_LOCATION_ADDRESS','address');
define('MAIL_TO_KEY', 'mailto');

$dotenv = Dotenv\Dotenv::create(__DIR__);
$dotenv->load();
$dotenv->required([
    'SMTP_SERVER',
    'SMTP_PORT',
    'SMTP_AUTH',
    'SMTP_LOGIN',
    'SMTP_PASSWORD',
    'SMTP_SECURE',
    'SMTP_FROM',
    'SMTP_MAIL_SUBJECT'
]);
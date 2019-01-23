<?php
require_once __DIR__.'/lib.php';

$data = [];
$json = json_decode(file_get_contents('php://input', true));

if ($json) {
    // close the connection before processing
    ob_end_clean();
    header("Connection: close");
    ignore_user_abort(); // optional
    ob_start();
    if ($json) {
        header('Content-Type: application/json');
        echo json_encode(['success' => true]);
    } else {
        header("HTTP/1.0 405 Method Not Allowed");
        die();
    }
    $size = ob_get_length();
    header("Content-Length: $size");
    ob_end_flush();
    flush();
    if (PHP_SAPI === 'fpm-fcgi') {
        fastcgi_finish_request();
    }
    // Do processing here
    $data = (array) $json;
}
if (array_key_exists('mailto', $data) ) {
    $mailto = [$data['mailto']];
    $toSend = getMailBody($data);
    sendSmtpMail($mailto, MAIL_USER, MAIL_NAME, MAIL_SUBJECT, $toSend);
} else {
    header("HTTP/1.0 405 Method Not Allowed");
    die();
}
if ($json) {
    $data = (array) $json;
    $data['log_datetime'] = date('Y-m-d H:i:s');
    $json_data = json_encode($data, JSON_UNESCAPED_UNICODE);
    logData($json_data);
}

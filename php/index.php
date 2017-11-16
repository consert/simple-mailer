<?php
require_once __DIR__.'/lib.php';

header('Content-Type: application/json');
$target = __DIR__.'/message.json';

$data = [];
$json = json_decode(file_get_contents('php://input', true));

// ensure we have a json file to read it's contents
if (!file_exists($target)) {
    file_put_contents($target,json_encode($data, JSON_UNESCAPED_UNICODE));
}

// close the connection before processing
ob_end_clean();
header("Connection: close");
ignore_user_abort(); // optional
ob_start();
if ($json) {
    echo json_encode(['success' => true]);
} else {
    $data = file_get_contents($target);
    echo $data;
}
$size = ob_get_length();
header("Content-Length: $size");
ob_end_flush();
flush();
if (PHP_SAPI === 'fpm-fcgi') {
    fastcgi_finish_request();
}

// Do processing here
if ($json) {
    $data = (array) $json;
    $json_data = json_encode($data, JSON_UNESCAPED_UNICODE);
    file_put_contents($target,$json_data);
}
if (array_key_exists('mailto', $data) ) {
    $mailto = [$data['mailto']];
    $toSend = json_encode($data, JSON_UNESCAPED_UNICODE);
    sendSmtpMail($mailto, MAIL_USER, MAIL_NAME, MAIL_SUBJECT, $toSend);
} else {
    $data = file_get_contents($target);
    echo $data;
}
if ($json) {
    $data = (array) $json;
    $json_data = json_encode($data, JSON_UNESCAPED_UNICODE);
    logData($json_data);
}
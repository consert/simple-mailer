<?php
require __DIR__.'/phpmailer/PHPMailerAutoload.php';
require_once  __DIR__.'/config.php';

function sendSmtpMail($to, $from, $from_name, $subject, $body) {
    $mail = new PHPMailer();
    $mail->CharSet = 'UTF-8';
    $mail->isSMTP();
    $mail->SMTPDebug = 0;
    $mail->SMTPAuth = true;
    $mail->SMTPSecure = 'tls';
    $mail->Host = 'smtp.gmail.com';
    $mail->Port = 587;
    $mail->Username = MAILUSER;
    $mail->Password = MAILPASS;
    $mail->setFrom($from, $from_name);
    $mail->Subject = $subject;
    $mail->Body = $body;
    foreach ($to as $resp) {
        $mail->addAddress($resp);
    }
    if(!$mail->send()) {
        return false;
    } else {
        return true;
    }
}

header('Content-Type: application/json');
$target = __DIR__.'/message.json';

$data = [];
$json = json_decode(file_get_contents('php://input', true));
if ($json) {
    $data = (array) $json;
    file_put_contents($target,json_encode($data, JSON_UNESCAPED_UNICODE));
}
if (!file_exists($target)) {
    file_put_contents($target,json_encode($data, JSON_UNESCAPED_UNICODE));
}
if (array_key_exists('mailto', $data) ) {
    $mailto = [$data['mailto']];
    $toSend = json_encode($data, JSON_UNESCAPED_UNICODE);
    if (sendSmtpMail($mailto, MAILUSER, MAILNAME, MAILSUBJECT, $toSend)) {
    $data = file_get_contents($target);
        echo json_encode(['success' => false]);
    } else {
        header('Internal Server Error', true,500);
        echo json_encode(['success' => false]);
    }
} else {
    $data = file_get_contents($target);
    echo $data;
}

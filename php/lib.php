<?php

require __DIR__.'/phpmailer/PHPMailerAutoload.php';
require_once  __DIR__.'/config.php';

function sendSmtpMail($to, $from, $from_name, $subject, $body) {
    $mail = new PHPMailer();
    $mail->CharSet = 'UTF-8';
    $mail->isSMTP();
    $mail->SMTPDebug = 0;
    $mail->SMTPAuth = SMTP_AUTH;
    $mail->SMTPSecure = SMTP_SECURE;
    $mail->Host = SMTP_HOST;
    $mail->Port = SMTP_PORT;
    $mail->Username = MAIL_USER;
    $mail->Password = MAIL_PASSWORD;
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

function logData($request_data){
    $data = date('Y-m-d H:i:s').PHP_EOL.$request_data.PHP_EOL;
    $file_head = 'log_';
    $file_ending = '.txt';
    $logs_dir = __DIR__.'/logs';

    if (!is_dir($logs_dir)) {
        mkdir($logs_dir, 0755, true);
    }
    $fi = new FilesystemIterator($logs_dir, FilesystemIterator::SKIP_DOTS);
    $files_in_dir = iterator_count($fi);
    $file_name = $file_head.'0'.$file_ending; // start with 0
    if ($files_in_dir > 0) { // log_0.txt already exists
        $file_name = $file_head. ($files_in_dir - 1) . $file_ending; // get the name of the last file)
        if (file_exists($logs_dir . '/' . $file_name)) {
            $last_file_size = filesize($logs_dir . '/' . $file_name); // check file's size
            // if we have more than 2MB on the file , create a new one //1048576
            if ($last_file_size > 1048576 * 2) {
                $file_name = $file_head. ($files_in_dir) . $file_ending;
            }
        }
    }
    // we got the file path, the name, and the data, write the file
    writeDataToFile($logs_dir,$file_name,$data);
}


function writeDataToFile($file_path, $file_name, $new_data) {
    $final_file = $file_path . '/' . $file_name;
    $temp_file = $file_path . '/tmp';
    if (!file_exists($final_file)) {
        file_put_contents($final_file,$new_data);
        chmod($final_file,0755);
    } else {
        $source = fopen($final_file, 'r');
        $temp = fopen($temp_file, 'w');
        while (!feof($source)) {
            $buffer = fread($source, 512);
            fwrite($temp, $buffer);
        }
        fwrite($temp,  $new_data);
        fclose($temp);
        fclose($source);
        rename($temp_file, $final_file);
        chmod($final_file,0644);
    }
}
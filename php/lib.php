<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
require 'vendor/autoload.php';
require_once  __DIR__.'/config.php';

/**
 * Sends email using smtp (phpmailer)
 *
 * @param array: $to: the recipient(s)
 * @param string: $from: the sender's email
 * @param string: $from_name: the sender's name
 * @param string: $subject: the mail's subject
 * @param string: $body: the mail's body
 * @return bool: if mail is successfully sent
 */
function sendSmtpMail($to, $from, $from_name, $subject, $body) {
    try {
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
        $mail->send();
        return true;
    } catch (Exception $e) {
        logData($e->in);
        return false;
    }
}

/**
 * Returns the address or the coordinates or null if any of the above found in the input array
 *
 * @param $locationArray
 * @return null|string
 */
function getLocationString($locationArray) {
    $location = null;
    if (array_key_exists(KEY_LOCATION_ADDRESS, $locationArray)) {
        $address = (string)$locationArray[KEY_LOCATION_ADDRESS];
        if (strtolower($address) !== KEY_LOCATION_UNKNOWN) {
            $location = $locationArray[KEY_LOCATION_ADDRESS];
        }
    }
    if (is_null($location) &&
        array_key_exists(KEY_LOCATION_LATITUDE, $locationArray) &&
        array_key_exists(KEY_LOCATION_LONGITUDE,$locationArray) &&
        floatval($locationArray[KEY_LOCATION_LATITUDE]) !== 0 &&
        floatval($locationArray[KEY_LOCATION_LONGITUDE]) != 0) {
            $location = KEY_LOCATION_LATITUDE.': '.$locationArray[KEY_LOCATION_LATITUDE] .
                ', '.KEY_LOCATION_LONGITUDE. ': '.$locationArray[KEY_LOCATION_LONGITUDE];
    }
    return $location;
}

/**
 * Returns a string containing the body of a message to be sent
 *
 * @param $postedData: the array that was posted
 * @return string
 */
function getMailBody($postedData) {
    $data = $postedData;
    // Backwards compatibility
    if (array_key_exists('data', $postedData)){
        $data = $postedData['data'];
    }
    $message = null;
    $location = null;
    $eventDateTime = null;
    $data_keys = array_keys($data);
    if (in_array(KEY_MESSAGE, $data_keys)) {
        $message = $data[KEY_MESSAGE];
    }
    if (in_array(KEY_DATETIME, $data_keys)) {
        $message = (string)$data[KEY_DATETIME];
    }
    if (in_array(KEY_LOCATION, $data_keys)) {
        $postedLocation = $data[KEY_LOCATION];
        if (is_object($postedLocation)){
            $postedLocation = (array)($postedLocation);
        }
        $location = getLocationString($postedLocation);
    }
    $str = 'TRILLION Button Message: '.PHP_EOL. 'Datetime: ';
    $str .= $eventDateTime ? (string)$eventDateTime : date('Y-m-d H:i:s').PHP_EOL.'Location: ';
    $str .= (!is_null($location) && strlen((string) ($location)) > 0) ? $location : 'Unknown';
    return $str . PHP_EOL.'Message: "'. $message . '"'.PHP_EOL;
}

/**
 * writes a string containing all the posted data
 * in the file: __DIR__.'/logs/log_#.txt, # is auto incremented every 2mb
 *
 * @param $data
 */
function logData($data){
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
    writeDataToFile($logs_dir,$file_name,$data.PHP_EOL);
}


/**
 * Writes data to a file (helper function of the above(logData)
 *
 * @param $file_path
 * @param $file_name
 * @param $new_data
 */
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

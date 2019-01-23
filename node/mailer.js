'use strict';

const nodemailer = require('nodemailer');

const config = require('./config');

const transporter = nodemailer.createTransport(config.mailConfig);

const getLocationString = (locationObject) => {
  if (config.KEY_LOCATION_ADDRESS in locationObject){
    const locationAddress = locationObject[config.KEY_LOCATION_ADDRESS];
    if (locationAddress.toLowerCase() !== (config.KEY_LOCATION_UNKNOWN)) {
      return locationAddress;
    }
  }
  if (config.KEY_LOCATION_LATITUDE in locationObject &&
      config.KEY_LOCATION_LONGITUDE in locationObject){
    const latitude = locationObject[config.KEY_LOCATION_LATITUDE];
    const longitude = locationObject[config.KEY_LOCATION_LONGITUDE];
    if (parseFloat(latitude) !== 0 && parseFloat(longitude) !== 0) {
      return `${config.KEY_LOCATION_LATITUDE}: ${locationObject[config.KEY_LOCATION_LATITUDE]}${config.KEY_LOCATION_LONGITUDE}: ${locationObject[config.KEY_LOCATION_LONGITUDE]}`
    }
  }
  return null
};

module.exports = {
  getBody: (json) => {
    let body = '';
    let parts = json;
    // Backwards compatibility
    if ('data' in json) {
      parts = json['data'];
    }
    // parts.keys
    body += 'TRILLION Button Message: \nDatetime: ';
    if (config.KEY_DATETIME in parts) {
      body += `${parts[config.KEY_DATETIME]},\n`;
    } else {
      body += new Date().toString();
      body += '\n';
    }
    body += 'Location: ';
    if (config.KEY_LOCATION in parts){
      const locationString = getLocationString(parts[config.KEY_LOCATION]);
      if (locationString !== null && locationString.length > 1) {
        body += `${locationString}\n`;
      } else {
        body += 'Unknown\n';
      }
    } else{
      body += 'Unknown\n';
    }
    body += 'Message: ';
    if (config.KEY_MESSAGE in parts){
      body += `"${parts[config.KEY_MESSAGE]}"`;
    }
    return body;
  },
  send: (receiver, text, then) => {
    transporter.sendMail({
      from: `${config.mailerName} <${config.mailConfig.auth.user}>`,
      to: receiver,
      subject: config.mailSubject,
      text
    }, (err, info) => {
      then(err,info)
    });
  }
};

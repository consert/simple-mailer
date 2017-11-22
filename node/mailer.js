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
    if ('data' in json) {
      parts = json['data'];
    }
    // parts.keys
    if (config.KEY_ANONYMOUS in parts && parts[config.KEY_ANONYMOUS] === true) {
      body += 'A user with hidden id\n'
    } else if (config.KEY_USER in parts) {
      body += `The user with the button ${parts[config.KEY_USER]},\n`
    }
    body += 'has sent on ';
    if (config.KEY_EVENT_DATETIME in parts) {
      body += `${parts[config.KEY_EVENT_DATETIME]},\n`;
    } else {
      body += new Date().toString();
      body += ',\n';
    }
    body += 'from ';
    if (config.KEY_LOCATION in parts){
      const locationString = getLocationString(parts[config.KEY_LOCATION]);
      if (locationString) {
        body += `location: ${locationString},\n`
      } else {
        body += 'an unknown location,\n'
      }
    }
    body += 'the message: \n';
    if (config.KEY_DESCRIPTION in parts){
      body += `"${parts[config.KEY_DESCRIPTION]}"`;
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


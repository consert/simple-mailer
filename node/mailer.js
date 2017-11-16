'use strict';

const nodemailer = require('nodemailer');

const config = require('./config');

const transporter = nodemailer.createTransport(config.mailConfig);

module.exports = {
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


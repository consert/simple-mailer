module.exports = {
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
};
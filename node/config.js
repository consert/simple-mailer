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
  mailSubject: 'Mail Subject',
  KEY_ANONYMOUS: 'anonymous',
  KEY_USER: 'user',
  KEY_DESCRIPTION: 'description',
  KEY_EVENT_DATETIME: 'eventDateTime',
  KEY_LOCATION: 'location',
  KEY_LOCATION_UNKNOWN: 'unknown',
  KEY_LOCATION_LATITUDE: 'latitude',
  KEY_LOCATION_LONGITUDE: 'longitude',
  KEY_LOCATION_ADDRESS: 'address'
};
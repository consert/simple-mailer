'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const logger = require('./logger');

const app = express();
app.use(bodyParser.json());

app.get('/', (req,res) => {
  res.send(405, 'Method Not Allowed');
});


app.post('/', (req, res) => {
  res.set('Content-Type', 'application/json');
  let mailto = req.query['mailto'];
  if (!mailto) {
    mailto = null;
  }
  const body = req.body;
  res.status(200).json({success: true});
  logger.logData(body);
  if (body['mailto']) {
    mailto = body['mailto'];
  }
  if (mailto !== null) {
    const mailer = require('./mailer');
    const mailBody = mailer.getBody(body);
    mailer.send( mailto, mailBody, (err)=> {
      if (err) {logger.logData(err);}
    })
  }
});

// error handling
app.use((err, req, res, next) =>{
  if (err) {
    logger.logData(err);
    res.status(err.status).json({error: err.message});
  }
  next();
});


app.listen(3000, function (err) {
  if (err) {
    throw err
  }
  console.log('Server started on port 3000')
});


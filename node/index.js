'use strict';

const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());


// Testing only: send last received message
app.get('/', (req,res) => {
  res.set('Content-Type', 'application/json');
  fs.readFile('./message.json', {encoding: 'utf8'}, (err, data) => {
    if (!err) {
      res.json(JSON.parse(data));
    } else {
      res.json({});
    }
  });
});


app.post('/', (req, res) => {
  res.set('Content-Type', 'application/json');
  const body = req.body;
  if (body['mailto']) {
    const mailer = require('./mailer');
    mailer.send( body['mailto'], JSON.stringify(body), (err, info)=> {
      if (err) {
        res.status(500).json({success: false})
      } else {
        fs.writeFile('./message.json', JSON.stringify(body), {encoding: 'utf8'}, (err) => {
          if (err) {
            res.status(500).json({success: false})
          }
          else {
            res.status(200).json({success: true});
          }
        });
      }
    })
  } else {
    res.status(200).json({success: true});
  }
});


// error handling
app.use((err, req, res, next) =>{
  if (err) {
    console.log(err);
    res.status(err.status).json({error: err.message});
  }
});


app.listen(3000, function (err) {
  if (err) {
    throw err
  }
  console.log('Server started on port 3000')
});


const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const logFilePath = path.join(__dirname, '../logs/app.log');

router.get('/', (req, res) => {
  res.render('maintenance');
});

router.get('/logs', (req, res) => {
  fs.readFile(logFilePath, 'utf8', (err, data) => {
    if (err) {
      res.status(500).send('Unable to read log file.');
      return;
    }
    res.send(data);
  });
});

module.exports = router;

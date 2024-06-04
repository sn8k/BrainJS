const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.render('maintenance', { title: 'Maintenance' });
});

module.exports = router;

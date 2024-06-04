const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');

const modulesPath = path.join(__dirname, '..', 'modules');

// Endpoint pour lister les modules installés
router.get('/', (req, res) => {
  const modules = fs.readdirSync(modulesPath).filter(file => fs.lstatSync(path.join(modulesPath, file)).isDirectory());
  res.render('modules', { title: 'Modules', modules });
});

// Endpoint pour afficher un module spécifique
router.get('/:module', (req, res) => {
  const moduleName = req.params.module;
  const modulePath = path.join(modulesPath, moduleName);
  if (fs.existsSync(modulePath) && fs.lstatSync(modulePath).isDirectory()) {
    res.sendFile(path.join(modulePath, 'index.html'));
  } else {
    res.status(404).send('Module not found');
  }
});

module.exports = router;

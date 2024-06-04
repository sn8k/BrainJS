const express = require('express');
const router = express.Router();
const multer = require('multer');
const tar = require('tar');
const fsExtra = require('fs-extra');
const path = require('path');
const logger = require('../logger');

// Version de l'application
const version = '1.0';

const upload = multer({ dest: 'uploads/' });

// Page principale du tableau de bord
router.get('/', (req, res) => {
  res.render('dashboard', { version });
});

// Route pour afficher la page de gestion des modules
router.get('/modules', (req, res) => {
  const modulesPath = path.join(__dirname, '../modules');
  const modules = fsExtra.readdirSync(modulesPath);
  res.render('modules', { modules, version });
});

// Route pour lister les modules installés
router.get('/modules/list', (req, res) => {
  const modulesPath = path.join(__dirname, '../modules');
  const modules = fsExtra.readdirSync(modulesPath);
  res.json(modules);
});

// Route pour uploader et installer un module
router.post('/upload', upload.single('module'), (req, res) => {
  const filePath = req.file.path;
  const moduleName = req.file.originalname.replace('.tar.gz', '');
  const extractPath = path.join(__dirname, '../modules', moduleName);

  fsExtra.ensureDir(extractPath)  // Assurer que le répertoire de destination existe
    .then(() => {
      return tar.x({
        file: filePath,
        cwd: extractPath
      });
    })
    .then(() => {
      fsExtra.removeSync(filePath);
      logger.info(`Module ${req.file.originalname} installed successfully.`);
      res.redirect('/modules');
    })
    .catch(err => {
      logger.error(`Error extracting module: ${err.message}`);
      res.status(500).send('Error extracting module.');
    });
});

// Route pour désinstaller un module
router.post('/delete', (req, res) => {
  const moduleName = req.body.moduleName;
  const modulePath = path.join(__dirname, '../modules', moduleName);

  fsExtra.remove(modulePath)
    .then(() => {
      logger.info(`Module ${moduleName} deleted successfully.`);
      res.redirect('/modules');
    })
    .catch(err => {
      logger.error(`Error deleting module: ${err.message}`);
      res.status(500).send('Error deleting module.');
    });
});

module.exports = router;

const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const winston = require('winston');
const app = express();
const port = 3000;

// Version de l'application
const version = '1.0';

// Configuration des logs
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `${timestamp} ${level}: ${message}`;
    })
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/app.log' }),
    new winston.transports.Console()
  ]
});

// Configuration de body-parser
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Middleware pour injecter la version dans toutes les vues
app.use((req, res, next) => {
  res.locals.version = version;
  next();
});

// Configuration de EJS pour les vues
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Configuration des fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Routes
const indexRouter = require('./routes/index');
const maintenanceRouter = require('./routes/maintenance');
app.use('/', indexRouter);
app.use('/maintenance', maintenanceRouter);

// Charger dynamiquement les modules installés
const modulesPath = path.join(__dirname, 'modules');
fs.readdirSync(modulesPath).forEach(module => {
  const modulePath = path.join(modulesPath, module);
  const moduleIndexPath = path.join(modulePath, 'index.js');
  if (fs.lstatSync(modulePath).isDirectory() && fs.existsSync(moduleIndexPath)) {
    const moduleRouter = require(modulePath);
    const routePath = `/modules/${encodeURIComponent(module)}`;
    app.use(routePath, moduleRouter);
  }
});

// Démarrage du serveur
app.listen(port, () => {
  logger.info(`Server running at http://localhost:${port}/`);
});

const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const fsExtra = require('fs-extra');
const winston = require('winston');
const session = require('express-session');
const ini = require('ini');
const { execSync } = require('child_process');
const app = express();
const port = 3000;

// Version de l'application
const version = '1.0.4';

// Fonction pour vérifier et installer les dépendances
const checkDependencies = () => {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
  const dependencies = packageJson.dependencies || {};
  const missingDependencies = [];

  for (const dep in dependencies) {
    try {
      require.resolve(dep);
    } catch (e) {
      missingDependencies.push(dep);
    }
  }

  if (missingDependencies.length > 0) {
    console.log('Installing missing dependencies:', missingDependencies.join(', '));
    execSync(`npm install ${missingDependencies.join(' ')}`, { stdio: 'inherit' });
  }
};

// Vérifier les dépendances avant de démarrer le serveur
checkDependencies();

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

// Middleware pour les sessions
app.use(session({
  secret: 'your_secret_key',
  resave: false,
  saveUninitialized: true
}));

// Middleware pour injecter la version dans toutes les vues
app.use((req, res, next) => {
  res.locals.version = version;
  res.locals.title = 'BrainJS';  // Titre par défaut
  res.locals.bodyClass = '';     // Classe du corps par défaut
  res.locals.user = req.session.user;
  next();
});

// Configuration de EJS pour les vues
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Configuration des fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Charger les informations d'identification
const config = ini.parse(fs.readFileSync('config.ini', 'utf-8'));
const credentials = config.credentials;

// Route pour afficher la page de login
app.get('/login', (req, res) => {
  res.render('login', { title: 'Login', bodyClass: '', error: null });
});

// Route pour gérer la soumission du formulaire de login
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === credentials.username && password === credentials.password) {
    req.session.user = username;
    res.redirect('/');
  } else {
    res.render('login', { error: 'Invalid username or password', title: 'Login', bodyClass: '' });
  }
});

// Middleware pour protéger les routes
const authMiddleware = (req, res, next) => {
  if (!req.session.user) {
    res.redirect('/login');
  } else {
    next();
  }
};

// Routes protégées
const indexRouter = require('./routes/index');
const maintenanceRouter = require('./routes/maintenance');
const modulesRouter = require('./routes/modules'); // Ajout d'un routeur pour les modules

app.use('/', authMiddleware, (req, res, next) => {
  res.locals.title = 'Dashboard';
  next();
}, indexRouter);
app.use('/maintenance', authMiddleware, (req, res, next) => {
  res.locals.title = 'Maintenance';
  next();
}, maintenanceRouter);
app.use('/modules', authMiddleware, modulesRouter); // Utiliser le routeur pour les modules

// Démarrage du serveur
app.listen(port, () => {
  logger.info(`Server running at http://localhost:${port}/`);
});

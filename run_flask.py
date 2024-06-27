# run_flask.py - Version 1.5
# Emplacement: run_flask.py

import os
import sys
from gpt4all import GPT4All

# Définir le répertoire racine du projet
project_root = os.path.dirname(os.path.abspath(__file__))

# Définir le répertoire backend
backend_dir = os.path.join(project_root, 'backend')

# Changer le répertoire de travail actuel pour le répertoire backend
os.chdir(backend_dir)

# Ajout du répertoire `backend` au `sys.path`
sys.path.append(backend_dir)

from app import app  # Import direct du fichier app.py dans le répertoire backend

# Mettre à jour les chemins relatifs pour les logs et les données
#os.environ['DATA_DIR'] = os.path.join(project_root, 'data')
#os.environ['LOG_DIR'] = os.path.join(project_root, 'logs')
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Activer le mode debug

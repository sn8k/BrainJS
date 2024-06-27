# run_flask.py - Version 2.0
# Emplacement: backend/run_flask.py

import os
import sys

# Définir le répertoire racine du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ajouter le répertoire `backend` au `sys.path`
sys.path.append(project_root)

# Mettre à jour les chemins relatifs pour les logs et les données
os.environ['DATA_DIR'] = os.path.join(project_root, 'data')
os.environ['LOG_DIR'] = os.path.join(project_root, 'logs')
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

from backend.app import app  # Import direct du fichier app.py dans le répertoire backend

if __name__ == "__main__":
    # Exécuter l'application Flask avec le mode debug
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)  # Désactiver le reloader automatique

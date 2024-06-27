# app.py - Version 3.4
# Emplacement: backend/app.py

import os
import json
import subprocess
import sys
import numpy as np
import tensorflow as tf
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from backend.routes.dashboard import dashboard_bp
from backend.routes.neurons_connections import neurons_connections_bp
from backend.routes.learning_memory import learning_memory_bp
from backend.routes.perception_sensory import perception_sensory_bp
from backend.routes.cognition_decision import cognition_decision_bp
from backend.routes.emotions_social import emotions_social_bp
from backend.routes.language_communication import language_communication_bp
from backend.routes.logs_monitoring import logs_monitoring_bp
from backend.routes.settings import settings_bp, settings_general_bp, settings_neural_network_bp, settings_video_sources_bp, settings_database_bp, settings_debug_bp
from backend.routes.settings_folders import settings_folders_bp
from backend.routes.view import view_bp
from backend.routes.file_learning import file_learning_bp
from backend.routes.network import network_bp
from backend.models import init_db, db, Config
from backend.brain_model import BrainModel
from backend.log_manager import LogManager
from backend.logging_config import setup_logging
from backend.gpt4all_manager import initialize_gpt4all, generate_response
import nmap

# Function to install required packages
def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

# Install requirements before initializing the app
install_requirements()

# Disable oneDNN custom operations to avoid numerical errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configure Flask app and specify the template and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backups'))
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{data_dir}/network_scan_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

# Set the secret key to some random bytes
app.secret_key = os.urandom(24)

# Initialize the database
init_db(app)

# Configure Flask-Migrate
migrate = Migrate(app, db)

# Setup logging
setup_logging()

# Ensure log directory exists
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Ensure backup directory exists
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Ensure data directory exists
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Load the configuration file
def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json'))
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "video_sources": ["http://www.insecam.org/", "https://www.earthcam.com/"],
        "selected_source": "http://www.insecam.org/",
        "chromium_path": "",
        "data_dir": data_dir,
        "log_dir": log_dir
    }

with app.app_context():
    config = load_config()

# Enregistrement des blueprints
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(neurons_connections_bp, url_prefix='/neurons_connections')
app.register_blueprint(learning_memory_bp, url_prefix='/learning_memory')
app.register_blueprint(perception_sensory_bp, url_prefix='/perception_sensory')
app.register_blueprint(cognition_decision_bp, url_prefix='/cognition_decision')
app.register_blueprint(emotions_social_bp, url_prefix='/emotions_social')
app.register_blueprint(language_communication_bp, url_prefix='/language_communication')
app.register_blueprint(logs_monitoring_bp, url_prefix='/logs_monitoring')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(settings_general_bp, url_prefix='/settings/general')
app.register_blueprint(settings_neural_network_bp, url_prefix='/settings/neural_network')
app.register_blueprint(settings_video_sources_bp, url_prefix='/settings/video_sources')
app.register_blueprint(settings_database_bp, url_prefix='/settings/database')
app.register_blueprint(settings_debug_bp, url_prefix='/settings/debug')
app.register_blueprint(settings_folders_bp, url_prefix='/settings/folders')
app.register_blueprint(view_bp, url_prefix='/view')
app.register_blueprint(file_learning_bp, url_prefix='/file_learning')
app.register_blueprint(network_bp, url_prefix='/network')

brain = BrainModel()
log_manager = LogManager()  # Suppression du paramètre log_dir

# Charger le modèle au démarrage
tf_model = None
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model.h5')
if os.path.exists(model_path):
    tf_model = tf.keras.models.load_model(model_path)
    print(f"Modèle chargé depuis {model_path}")

# Initialiser GPT4All
chatbot = None
if __name__ == '__main__':
    model_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    chatbot = initialize_gpt4all(model_directory)

@app.route('/')
def index():
    return redirect(url_for('dashboard.index'))

@app.route('/network_status', methods=['GET'])
def network_status():
    return jsonify(brain.get_network_status())

@app.route('/neuron_function_count', methods=['GET'])
def neuron_function_count():
    return jsonify({
        'neuron_count': brain.get_neuron_count(),
        'function_count': brain.get_function_count()
    })

@app.route('/performance_metrics', methods=['GET'])
def performance_metrics():
    return jsonify(brain.get_performance_metrics())

@app.route('/training_progress', methods=['GET'])
def training_progress():
    return jsonify(brain.get_training_progress())

@app.route('/logs', methods=['GET'])
def logs():
    return jsonify(log_manager.get_logs())

@app.route('/backup_db', methods=['GET'])
def backup_db():
    backup_file = os.path.join(backup_dir, 'network_scan_results_backup.db')
    db.session.commit()  # Assurez-vous que toutes les transactions sont terminées
    db.engine.execute(f"VACUUM INTO '{backup_file}'")
    flash('Sauvegarde de la base de données effectuée avec succès.', 'success')
    return send_from_directory(directory=backup_dir, path='network_scan_results_backup.db', as_attachment=True)

@app.route('/restore_db', methods=['POST'])
def restore_db():
    if 'backup_file' not in request.files:
        flash('Aucun fichier de sauvegarde sélectionné.', 'danger')
        return redirect(url_for('settings_database.database'))

    file = request.files['backup_file']
    if file.filename == '':
        flash('Aucun fichier de sauvegarde sélectionné.', 'danger')
        return redirect(url_for('settings_database.database'))

    backup_file_path = os.path.join(backup_dir, secure_filename(file.filename))
    file.save(backup_file_path)
    db.drop_all()
    db.create_all()
    db.engine.execute(f"ATTACH DATABASE '{backup_file_path}' AS backup")
    db.engine.execute("INSERT INTO main.sqlite_master SELECT * FROM backup.sqlite_master")
    db.engine.execute("DETACH DATABASE backup")
    flash('Restauration de la base de données effectuée avec succès.', 'success')
    return redirect(url_for('settings_database.database'))

@app.route('/start_training', methods=['POST'])
def start_training():
    # Code pour démarrer l'entraînement
    inputs = np.random.rand(10, 3)  # Exemples de données d'entrée
    outputs = np.random.randint(0, 2, size=(10, 1))  # Exemples de données de sortie
    brain.train(inputs, outputs)
    flash('Entraînement démarré avec succès.', 'success')
    return redirect(url_for('dashboard.index'))

@app.route('/stop_training', methods=['POST'])
def stop_training():
    # Code pour arrêter l'entraînement
    brain.stop_training()
    flash('Entraînement arrêté avec succès.', 'success')
    return redirect(url_for('dashboard.index'))

@app.route('/language_communication/process_text', methods=['POST'])
def process_text():
    if not chatbot:
        return jsonify({"response": "Erreur : Le chatbot n'est pas disponible."})

    data = request.get_json()
    message = data.get('text', '')

    response = generate_response(chatbot, message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Activer le mode debug

# Fin du fichier app.py - Version 3.4

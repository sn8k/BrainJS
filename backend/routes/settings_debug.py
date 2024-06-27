# settings_debug.py - Version 1.4
# Emplacement: backend/routes/settings_debug.py

from flask import Blueprint, render_template, jsonify, request
import os
import sys
import logging
import shutil
from backend.app import db, tf_model  # Importation du modèle TensorFlow et de la base de données

settings_debug_bp = Blueprint('settings_debug', __name__)

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
log_file_path = os.path.join(log_dir, 'main.log')

@settings_debug_bp.route('/debug', methods=['GET', 'POST'])
def debug():
    if request.method == 'POST':
        if 'clear_logs' in request.form:
            clear_logs()
        elif 'clear_memory' in request.form:
            clear_data()
        elif 'full_reset' in request.form:
            full_reset()
    return render_template('settings_debug.html')

def clear_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, 'w'):
            pass
        logging.info("Logs cleared")

def clear_data():
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')
        logging.info("Data directory cleared")

def full_reset():
    clear_logs()
    clear_data()
    db.drop_all()
    db.create_all()
    logging.info("Full reset performed")

@settings_debug_bp.route('/fix_absl_metrics', methods=['POST'])
def fix_absl_metrics():
    if tf_model:
        # Compile the model with dummy metrics to satisfy absl requirements
        tf_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        logging.info("Metrics fixed successfully")
        return jsonify({"status": "Metrics fixed successfully"})
    else:
        logging.error("Model not loaded")
        return jsonify({"status": "Model not loaded"}), 404

@settings_debug_bp.route('/restart_server', methods=['POST'])
def restart_server():
    try:
        # Logic to restart the server
        # The exact command may vary depending on your server setup
        logging.info("Server restart initiated")
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        logging.error(f"Failed to restart server. Reason: {e}")
        return jsonify({"status": "Failed to restart server"}), 500

# Fin du fichier settings_debug.py - Version 1.4

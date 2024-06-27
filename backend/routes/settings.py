# settings.py - Version 3.0
# Emplacement: backend/routes/settings.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
import json
import subprocess
import sys
import signal
import shutil
import tensorflow as tf
from werkzeug.utils import secure_filename
from backend.models import db

settings_bp = Blueprint('settings', __name__)
settings_general_bp = Blueprint('settings_general', __name__, url_prefix='/settings/general')
settings_neural_network_bp = Blueprint('settings_neural_network', __name__, url_prefix='/settings/neural_network')
settings_video_sources_bp = Blueprint('settings_video_sources', __name__, url_prefix='/settings/video_sources')
settings_database_bp = Blueprint('settings_database', __name__, url_prefix='/settings/database')
settings_debug_bp = Blueprint('settings_debug', __name__, url_prefix='/settings/debug')
settings_folders_bp = Blueprint('settings_folders', __name__, url_prefix='/settings/folders')

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'config.json'))
backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backups'))

def load_config():
    print(f"Loading config from: {config_path}")
    if os.path.exists(config_path):
        print(f"Config file found at {config_path}")
        with open(config_path, 'r') as f:
            config = json.load(f)
            if "video_sources" not in config:
                config["video_sources"] = ["http://www.insecam.org/", "https://www.earthcam.com/"]
            if "selected_source" not in config:
                config["selected_source"] = config["video_sources"][0]
            if "chromium_path" not in config:
                config["chromium_path"] = os.path.join(os.getcwd(), "chrome-win")
            if "data_dir" not in config:
                config["data_dir"] = os.path.join(os.getcwd(), 'data')
            if "log_dir" not in config:
                config["log_dir"] = os.path.join(os.getcwd(), 'logs')
            if "model_dir" not in config:
                config["model_dir"] = os.path.join(os.getcwd(), 'models')
            if "upload_dir" not in config:
                config["upload_dir"] = os.path.join(os.getcwd(), 'uploads')
            config["full_data_dir"] = os.path.abspath(config["data_dir"])
            config["full_log_dir"] = os.path.abspath(config["log_dir"])
            config["full_model_dir"] = os.path.abspath(config["model_dir"])
            config["full_upload_dir"] = os.path.abspath(config["upload_dir"])
            return config
    else:
        print(f"Config file not found. Creating new config at {config_path}")
        default_config = {
            "auto_learn": False,
            "video_sources": ["http://www.insecam.org/", "https://www.earthcam.com/"],
            "selected_source": "http://www.insecam.org/",
            "verbosity_level": "INFO",
            "neural_network_status": "active",
            "training_epochs": 10,
            "chromium_path": os.path.join(os.getcwd(), "chrome-win"),
            "discord_token": "",
            "discord_channel_id": "",
            "data_dir": os.path.join(os.getcwd(), 'data'),
            "log_dir": os.path.join(os.getcwd(), 'logs'),
            "model_dir": os.path.join(os.getcwd(), 'models'),
            "upload_dir": os.path.join(os.getcwd(), 'uploads'),
            "full_data_dir": os.path.abspath(os.path.join(os.getcwd(), 'data')),
            "full_log_dir": os.path.abspath(os.path.join(os.getcwd(), 'logs')),
            "full_model_dir": os.path.abspath(os.path.join(os.getcwd(), 'models')),
            "full_upload_dir": os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
        }
        save_config(default_config)
        return default_config

def save_config(config):
    print(f"Saving config to: {config_path}")
    with open(config_path, 'w') as f:
        json.dump(config, f)

@settings_general_bp.route('/', methods=['GET', 'POST'])
def general():
    config = load_config()
    if request.method == 'POST':
        if 'verbosity_level' in request.form:
            config['verbosity_level'] = request.form['verbosity_level']
            save_config(config)
        if 'discord_token' in request.form:
            config['discord_token'] = request.form['discord_token']
            save_config(config)
        if 'discord_channel_id' in request.form:
            config['discord_channel_id'] = request.form['discord_channel_id']
            save_config(config)
        if 'chromium_path' in request.form:
            config['chromium_path'] = request.form['chromium_path']
            save_config(config)
    return render_template('settings_general.html', config=config)

@settings_neural_network_bp.route('/', methods=['GET', 'POST'])
def neural_network():
    config = load_config()
    if request.method == 'POST':
        if 'neural_network_status' in request.form:
            config['neural_network_status'] = request.form['neural_network_status']
            save_config(config)
        if 'training_epochs' in request.form:
            config['training_epochs'] = int(request.form['training_epochs'] or 10)  # Default to 10 if empty
            save_config(config)
    return render_template('settings_neural_network.html', config=config)

@settings_video_sources_bp.route('/', methods=['GET', 'POST'])
def video_sources():
    config = load_config()
    if request.method == 'POST':
        if 'new_source' in request.form:
            new_source = request.form['new_source']
            if new_source not in config["video_sources"]:
                config["video_sources"].append(new_source)
                save_config(config)
        if 'remove_source' in request.form:
            remove_source = request.form['remove_source']
            if remove_source in config["video_sources"]:
                config["video_sources"].remove(remove_source)
                save_config(config)
        if 'selected_source' in request.form:
            config["selected_source"] = request.form['selected_source']
            save_config(config)
    return render_template('settings_video_sources.html', config=config)

@settings_database_bp.route('/', methods=['GET', 'POST'])
def database():
    if request.method == 'POST':
        if 'backup_db' in request.form:
            return backup_db()
        if 'restore_db' in request.form:
            return restore_db()
    return render_template('settings_database.html')

@settings_database_bp.route('/backup_db', methods=['GET'])
def backup_db():
    backup_file = os.path.join(backup_dir, 'network_scan_results_backup.db')
    db.session.commit()  # Assurez-vous que toutes les transactions sont terminées
    with db.engine.connect() as connection:
        connection.execute(f"VACUUM INTO '{backup_file}'")
    flash('Sauvegarde de la base de données effectuée avec succès.', 'success')
    return send_from_directory(directory=backup_dir, path='network_scan_results_backup.db', as_attachment=True)

@settings_database_bp.route('/restore_db', methods=['POST'])
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
    with db.engine.connect() as connection:
        connection.execute(f"ATTACH DATABASE '{backup_file_path}' AS backup")
        connection.execute("INSERT INTO main.sqlite_master SELECT * FROM backup.sqlite_master")
        connection.execute("DETACH DATABASE backup")
    flash('Restauration de la base de données effectuée avec succès.', 'success')
    return redirect(url_for('settings_database.database'))

@settings_debug_bp.route('/', methods=['GET', 'POST'])
def debug():
    if request.method == 'POST':
        if 'clear_memory' in request.form:
            clear_memory()
        if 'clear_logs' in request.form:
            clear_logs()
        if 'full_reset' in request.form:
            full_reset()
    return render_template('settings_debug.html')

def clear_memory():
    data_dir = os.path.join(os.getcwd(), 'data')
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    flash('Mémoire effacée avec succès.', 'success')

def clear_logs():
    log_dir = os.path.join(os.getcwd(), 'logs')
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
        os.makedirs(log_dir)
    flash('Logs effacés avec succès.', 'success')

def full_reset():
    clear_logs()
    clear_memory()
    db.drop_all()
    db.create_all()
    flash('Logs et mémoire effacés et base de données réinitialisée.', 'success')

@settings_debug_bp.route('/restart_server', methods=['POST'])
def restart_server():
    try:
        os.execv(sys.executable, ['python'] + sys.argv)
        return 'Server is restarting...'
    except Exception as e:
        flash(f'Erreur lors du redémarrage du serveur: {str(e)}', 'danger')
        return redirect(url_for('settings_debug.debug'))

@settings_debug_bp.route('/fix_absl_metrics', methods=['POST'])
def fix_absl_metrics():
    config = load_config()
    model_path = os.path.join(config["model_dir"], 'model.h5')
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.save(model_path)
        flash("Metrics fixed successfully.", 'success')
        return jsonify({"status": "Metrics fixed successfully"})
    else:
        flash("Model not loaded.", 'danger')
        return jsonify({"status": "Model not loaded"}), 404

@settings_folders_bp.route('/', methods=['GET', 'POST'])
def folders():
    config = load_config()
    if request.method == 'POST':
        print("Received POST request")
        print("Form Data:", request.form)
        if 'data_dir' in request.form:
            config['data_dir'] = request.form['data_dir']
        if 'log_dir' in request.form:
            config['log_dir'] = request.form['log_dir']
        if 'model_dir' in request.form:
            config['model_dir'] = request.form['model_dir']
        if 'upload_dir' in request.form:
            config['upload_dir'] = request.form['upload_dir']
        save_config(config)
        print("Config saved:", config)
    config["full_data_dir"] = os.path.abspath(config["data_dir"])
    config["full_log_dir"] = os.path.abspath(config["log_dir"])
    config["full_model_dir"] = os.path.abspath(config["model_dir"])
    config["full_upload_dir"] = os.path.abspath(config["upload_dir"])
    return render_template('settings_folders.html', config=config)

@settings_bp.route('/stop_project', methods=['POST'])
def stop_project():
    os.kill(os.getpid(), signal.SIGINT)
    return 'Stopping...'

# Fin du fichier settings.py - Version 3.0

# logs_monitoring.py - Version 1.4
# Emplacement: backend/routes/logs_monitoring.py

from flask import Blueprint, render_template, jsonify, send_from_directory, request
import os
import json
import psutil
import platform
import logging
import shutil
from backend.models import db
from datetime import datetime

logs_monitoring_bp = Blueprint('logs_monitoring', __name__)

# Fonction pour charger la configuration
def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'config.json'))
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "data_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data')),
        "log_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
    }

config = load_config()
data_dir = config.get("data_dir", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data')))
log_dir = config.get("log_dir", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs')))
log_file_path = os.path.join(log_dir, 'main.log')

# Ensure log directory exists
os.makedirs(log_dir, exist_ok=True)

# Initialize logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(message)s')

@logs_monitoring_bp.route('/')
def index():
    return render_template('logs_monitoring.html')

@logs_monitoring_bp.route('/data_files')
def data_files():
    files = os.listdir(data_dir)
    return jsonify(files)

@logs_monitoring_bp.route('/data_file/<filename>')
def data_file(filename):
    return send_from_directory(data_dir, filename)

@logs_monitoring_bp.route('/log_content')
def log_content():
    if not os.path.exists(log_file_path):
        open(log_file_path, 'w').close()  # Create the log file if it does not exist
    with open(log_file_path, 'r') as f:
        log_data = f.read()
    return jsonify(log_data.splitlines())

@logs_monitoring_bp.route('/system_info')
def system_info():
    system_data = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "ip_address": request.remote_addr,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
    return jsonify(system_data)

@logs_monitoring_bp.route('/clear_logs', methods=['POST'])
def clear_logs():
    with open(log_file_path, 'w'):
        pass
    return jsonify({"status": "Logs cleared"})

@logs_monitoring_bp.route('/clear_data', methods=['POST'])
def clear_data():
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    return jsonify({"status": "Data directory cleared"})

@logs_monitoring_bp.route('/reset_all', methods=['POST'])
def reset_all():
    clear_logs()
    clear_data()
    db.drop_all()
    db.create_all()
    return jsonify({"status": "Complete reset performed"})

# Fin du fichier logs_monitoring.py - Version 1.4

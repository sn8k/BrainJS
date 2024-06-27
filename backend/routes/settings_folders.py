# settings_folders.py - Version 2.1
# Emplacement: backend/routes/settings_folders.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from werkzeug.utils import secure_filename
from backend.models import db

settings_folders_bp = Blueprint('settings_folders', __name__, url_prefix='/settings/folders')

config_path = os.path.join(os.getcwd(), '..', 'data', 'config.json')

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            config["full_data_dir"] = os.path.abspath(config["data_dir"])
            config["full_log_dir"] = os.path.abspath(config["log_dir"])
            config["full_model_dir"] = os.path.abspath(config["model_dir"])
            config["full_upload_dir"] = os.path.abspath(config["upload_dir"])
            return config
    else:
        return {
            "data_dir": os.path.join(os.getcwd(), '..', 'data'),
            "log_dir": os.path.join(os.getcwd(), '..', 'logs'),
            "model_dir": os.path.join(os.getcwd(), '..', 'models'),
            "upload_dir": os.path.join(os.getcwd(), '..', 'uploads'),
            "full_data_dir": os.path.abspath(os.path.join(os.getcwd(), '..', 'data')),
            "full_log_dir": os.path.abspath(os.path.join(os.getcwd(), '..', 'logs')),
            "full_model_dir": os.path.abspath(os.path.join(os.getcwd(), '..', 'models')),
            "full_upload_dir": os.path.abspath(os.path.join(os.getcwd(), '..', 'uploads'))
        }

def save_config(config):
    with open(config_path, 'w') as f:
        json.dump(config, f)

@settings_folders_bp.route('/', methods=['GET', 'POST'])
def folders():
    config = load_config()
    if request.method == 'POST':
        if 'data_dir' in request.form:
            config['data_dir'] = request.form['data_dir']
        if 'log_dir' in request.form:
            config['log_dir'] = request.form['log_dir']
        if 'model_dir' in request.form:
            config['model_dir'] = request.form['model_dir']
        if 'upload_dir' in request.form:
            config['upload_dir'] = request.form['upload_dir']
        save_config(config)
    config["full_data_dir"] = os.path.abspath(config["data_dir"])
    config["full_log_dir"] = os.path.abspath(config["log_dir"])
    config["full_model_dir"] = os.path.abspath(config["model_dir"])
    config["full_upload_dir"] = os.path.abspath(config["upload_dir"])
    return render_template('settings_folders.html', config=config)

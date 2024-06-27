# language_communication.py - Version 2.1
# Emplacement: backend/routes/language_communication.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from backend.brain_model import BrainModel
from backend.models import NeuralData, db
from datetime import datetime
import json
import os

language_communication_bp = Blueprint('language_communication', __name__)
brain = BrainModel()

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'json', 'txt', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@language_communication_bp.route('/')
def index():
    dictionaries = os.listdir(UPLOAD_FOLDER)
    return render_template('language_communication.html', dictionaries=dictionaries)

@language_communication_bp.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    text = data.get('text')
    if text:
        response = brain.chat(text)
        
        neural_data = NeuralData(data_type='processed_text', data=json.dumps({'text': text, 'response': response}), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()

        return jsonify({'response': response})
    return jsonify({'status': 'Text is required'}), 400

@language_communication_bp.route('/upload_dictionary', methods=['POST'])
def upload_dictionary():
    if 'file' not in request.files:
        return jsonify({'status': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        brain.integrate_dictionaries()  # Intégrer le dictionnaire après le téléchargement
        return jsonify({'status': 'Dictionary uploaded successfully'})
    else:
        return jsonify({'status': 'Allowed file types are .json, .txt, .csv'})

@language_communication_bp.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'status': 'File uploaded successfully'})
    else:
        return jsonify({'status': 'Allowed file types are .json, .txt, .csv'})

# Fin du fichier language_communication.py - Version 2.1

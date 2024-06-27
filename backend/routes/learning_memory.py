# learning_memory.py - Version 1.3
# Emplacement: backend/routes/learning_memory.py

import json
from flask import Blueprint, render_template, request, jsonify
from backend.brain_model import BrainModel
from backend.models import NeuralData, db
from datetime import datetime

learning_memory_bp = Blueprint('learning_memory', __name__, url_prefix='/learning-memory')

brain = BrainModel()

@learning_memory_bp.route('/')
def index():
    return render_template('learning_memory.html')

@learning_memory_bp.route('/short-term-memory', methods=['POST'])
def short_term_memory():
    data = request.json
    brain.store_short_term_memory(data)
    
    neural_data = NeuralData(data_type='short_term', data=json.dumps(data), timestamp=datetime.utcnow())
    db.session.add(neural_data)
    db.session.commit()

    return jsonify({'status': 'Short term memory stored'})

@learning_memory_bp.route('/long-term-memory', methods=['POST'])
def long_term_memory():
    data = request.json
    brain.store_long_term_memory(data)
    
    neural_data = NeuralData(data_type='long_term', data=json.dumps(data), timestamp=datetime.utcnow())
    db.session.add(neural_data)
    db.session.commit()

    return jsonify({'status': 'Long term memory stored'})

# Fin du fichier learning_memory.py - Version 1.3

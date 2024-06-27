# perception_sensory.py - Version 1.3
# Emplacement: backend/routes/perception_sensory.py

from flask import Blueprint, render_template, request, jsonify
from backend.brain_model import BrainModel
from backend.models import NeuralData, db
from datetime import datetime
import json

perception_sensory_bp = Blueprint('perception_sensory', __name__, url_prefix='/perception-sensory')

brain = BrainModel()

@perception_sensory_bp.route('/')
def index():
    return render_template('perception_sensory.html')

@perception_sensory_bp.route('/vision', methods=['POST'])
def vision():
    data = request.json
    image_path = data.get('image_path')
    if image_path:
        result = brain.process_vision(image_path)
        
        neural_data = NeuralData(data_type='vision', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Image path required'}), 400

@perception_sensory_bp.route('/audition', methods=['POST'])
def audition():
    data = request.json
    audio_path = data.get('audio_path')
    if audio_path:
        result = brain.process_audition(audio_path)
        
        neural_data = NeuralData(data_type='audition', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Audio path required'}), 400

# Fin du fichier perception_sensory.py - Version 1.3

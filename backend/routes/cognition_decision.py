# cognition_decision.py - Version 1.9
# Emplacement: backend/routes/cognition_decision.py

from flask import Blueprint, render_template, request, jsonify
from backend.brain_model import BrainModel
from backend.models import NeuralData, db
from datetime import datetime
import json
from some_problem_solving_module import solve_astar, solve_dijkstra  # Vous devrez implémenter ou inclure ces modules

cognition_decision_bp = Blueprint('cognition_decision', __name__)

brain = BrainModel()

@cognition_decision_bp.route('/')
def index():
    return render_template('cognition_decision.html')

@cognition_decision_bp.route('/make_decision', methods=['POST'])
def make_decision():
    data = request.json
    decision_input = data.get('input')
    if decision_input:
        result = brain.make_decision(decision_input)
        
        neural_data = NeuralData(data_type='decision', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Input required'}), 400

@cognition_decision_bp.route('/solve_problem', methods=['POST'])
def solve_problem():
    data = request.json
    algorithm = data.get('algorithm')
    problem_data = data.get('problem_data')
    
    if algorithm == 'astar':
        result = solve_astar(problem_data)
    elif algorithm == 'dijkstra':
        result = solve_dijkstra(problem_data)
    else:
        return jsonify({'error': 'Algorithme invalide'}), 400
    
    return jsonify({'result': result})

@cognition_decision_bp.route('/learn', methods=['POST'])
def learn():
    data = request.json
    learning_input = data.get('input')
    if learning_input:
        result = brain.learn(learning_input)
        
        neural_data = NeuralData(data_type='learning', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Input required'}), 400

@cognition_decision_bp.route('/recognize_pattern', methods=['POST'])
def recognize_pattern():
    data = request.json
    pattern_input = data.get('input')
    if pattern_input:
        result = brain.recognize_pattern(pattern_input)
        
        neural_data = NeuralData(data_type='pattern_recognition', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Input required'}), 400

@cognition_decision_bp.route('/train_lstm', methods=['POST'])
def train_lstm():
    data = request.json
    series_data = data.get('input')
    if series_data:
        result = brain.train_lstm(series_data)
        
        neural_data = NeuralData(data_type='lstm_training', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Input required'}), 400

@cognition_decision_bp.route('/predict_lstm', methods=['POST'])
def predict_lstm():
    data = request.json
    input_data = data.get('input')
    if input_data:
        result = brain.predict_lstm(input_data)
        
        neural_data = NeuralData(data_type='lstm_prediction', data=json.dumps(data), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()
        
        return jsonify(result)
    return jsonify({'status': 'Input required'}), 400

# Fin du fichier cognition_decision.py - Version 1.9

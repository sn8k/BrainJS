# neurons_connections.py - Version 1.7
# Emplacement: backend/routes/neurons_connections.py

from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from backend.brain_model import BrainModel

neurons_connections_bp = Blueprint('neurons_connections', __name__)
brain = BrainModel()

@neurons_connections_bp.route('/')
def index():
    neurons = brain.get_neurons()
    connections = brain.get_neural_connections()
    return render_template('neurons_connections.html', neurons=neurons, connections=connections)

@neurons_connections_bp.route('/data')
def data():
    connections = brain.get_neural_connections()
    return jsonify(connections)

@neurons_connections_bp.route('/get_connections', methods=['GET'])
def get_connections():
    connections = brain.get_neural_connections()
    return jsonify(connections)

@neurons_connections_bp.route('/update_connection', methods=['POST'])
def update_connection():
    data = request.json
    source_id = data.get('source_id')
    target_id = data.get('target_id')
    weight = data.get('weight')
    brain.update_neural_connection(source_id, target_id, weight)
    return jsonify({'status': 'Connection updated successfully'})

@neurons_connections_bp.route('/add_connection', methods=['POST'])
def add_connection():
    data = request.form
    source_id = data.get('source_id')
    target_id = data.get('target_id')
    weight = float(data.get('weight'))
    brain.update_neural_connection(source_id, target_id, weight)
    return redirect(url_for('neurons_connections.index'))

# Fin du fichier neurons_connections.py - Version 1.7

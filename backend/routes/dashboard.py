# dashboard.py - Version 1.2
# Emplacement: backend/routes/dashboard.py

from flask import Blueprint, render_template, jsonify, request
from backend.brain_model import BrainModel

dashboard_bp = Blueprint('dashboard', __name__)

brain = BrainModel()

@dashboard_bp.route('/')
def index():
    network_status = brain.get_network_status()
    neuron_count = brain.get_neuron_count()
    function_count = brain.get_function_count()
    performance_metrics = brain.get_performance_metrics()
    training_progress = brain.get_training_progress()

    return render_template('dashboard.html',
                           network_status=network_status,
                           neuron_count=neuron_count,
                           function_count=function_count,
                           performance_metrics=performance_metrics,
                           training_progress=training_progress)

@dashboard_bp.route('/start_training', methods=['POST'])
def start_training():
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type"}), 415
    
    data = request.json
    # Vérifiez si les données sont correctes
    if not data or 'inputs' not in data or 'outputs' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    inputs = data['inputs']
    outputs = data['outputs']
    brain.start_training(inputs, outputs)
    return jsonify({"message": "Training started successfully"})

@dashboard_bp.route('/stop_training', methods=['POST'])
def stop_training():
    brain.stop_training()
    return jsonify({"message": "Training stopped successfully"})

# Fin du fichier dashboard.py - Version 1.2

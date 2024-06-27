# file_learning.py - Version 2.1
# Emplacement: backend/routes/file_learning.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json
import numpy as np
import onnx
import onnxruntime as ort
import tensorflow as tf
from werkzeug.utils import secure_filename
from backend.brain_model import BrainModel

file_learning_bp = Blueprint('file_learning', __name__)

upload_dir = os.path.join(os.getcwd(), 'uploads')
model_dir = os.path.join(os.getcwd(), 'models')
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

# Load the TensorFlow model
def load_model(model_path='model.h5'):
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path)
    return None

# Initialize the BrainModel and TensorFlow model
brain = BrainModel()
tf_model = load_model()
model_name = 'model.h5' if tf_model else None

@file_learning_bp.route('/', methods=['GET', 'POST'])
def index():
    global model_name
    model_loaded = model_name is not None
    return render_template('file_learning.html', model_loaded=model_loaded, model_name=model_name)

@file_learning_bp.route('/create_model', methods=['POST'])
def create_model():
    input_dim = int(request.form['input_dim'])
    hidden_layers = int(request.form['hidden_layers'])
    hidden_units = int(request.form['hidden_units'])
    
    # Create the model
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(hidden_units, activation='relu', input_shape=(input_dim,)))
    for _ in range(hidden_layers - 1):
        model.add(tf.keras.layers.Dense(hidden_units, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    
    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # Save the model
    model_path = os.path.join(model_dir, 'model.h5')
    model.save(model_path)
    
    global tf_model
    global model_name
    tf_model = model
    model_name = 'model.h5'
    
    flash("Le modèle a été créé et sauvegardé avec succès.", "success")
    return redirect(url_for('file_learning.index'))

@file_learning_bp.route('/load_model', methods=['POST'])
def load_model_route():
    if 'model_file' not in request.files:
        flash("Aucun fichier de modèle n'a été sélectionné.", "danger")
        return redirect(url_for('file_learning.index'))

    file = request.files['model_file']
    if file:
        filepath = os.path.join(model_dir, file.filename)
        file.save(filepath)
        global tf_model
        global model_name
        tf_model = load_model(filepath)
        model_name = file.filename
        flash(f"Le modèle {file.filename} a été chargé avec succès.", "success")
    else:
        flash("Aucun fichier de modèle n'a été sélectionné.", "danger")
    return redirect(url_for('file_learning.index'))

def process_file(filepath):
    try:
        if filepath.endswith('.onnx'):
            return process_onnx_file(filepath)
        elif filepath.endswith('.json'):
            return process_json_file(filepath)
        else:
            flash("Unsupported file format.", "danger")
            return False
    except Exception as e:
        print(f"Error processing file: {e}")
    return False

def process_onnx_file(filepath):
    try:
        # Load ONNX model
        onnx_model = onnx.load(filepath)
        onnx.checker.check_model(onnx_model)
        ort_session = ort.InferenceSession(filepath)
        
        # Get model input type and shape
        input_name = ort_session.get_inputs()[0].name
        input_type = ort_session.get_inputs()[0].type
        input_shape = ort_session.get_inputs()[0].shape

        # Prepare dummy input based on expected input type
        if 'int64' in input_type:
            dummy_input = np.random.randint(0, 100, size=input_shape).astype(np.int64)
        elif 'float' in input_type:
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
        else:
            print(f"Unsupported input type: {input_type}")
            return False
        
        # Run inference
        result = ort_session.run(None, {input_name: dummy_input})
        print(f"Inference result: {result}")

        # Convert result to training data and train the brain model
        inputs = dummy_input
        outputs = np.array(result).squeeze()

        brain.train(inputs, outputs)  # Train the brain with the ONNX model's output

        return True
    except Exception as e:
        print(f"Error processing ONNX file: {e}")
        return False

def process_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'inputs' in data and 'outputs' in data:
            inputs = data['inputs']
            outputs = data['outputs']
            
            if isinstance(inputs, list) and isinstance(outputs, list):
                inputs = np.array(inputs)
                outputs = np.array(outputs)
                
                # Vérifiez que les dimensions correspondent
                if inputs.ndim == 2 and len(inputs) == len(outputs):
                    brain.train(inputs, outputs)
                    return True
    except Exception as e:
        print(f"Error processing JSON file: {e}")
    
    return False

@file_learning_bp.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for('file_learning.index'))

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        if process_file(filepath):
            flash(f"Le fichier {filename} a été traité avec succès.", "success")
        else:
            flash(f"Erreur lors du traitement du fichier {filename}.", "danger")
    else:
        flash("Format de fichier non supporté.", "danger")
    return redirect(url_for('file_learning.index'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'onnx', 'json'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fin du fichier file_learning.py - Version 2.1

# brain_model.py - Version 2.8
# Emplacement: backend/brain_model.py

from model_utils import initialize_model, load_model, save_model, add_neurons_to_model
from data_manager import initialize_data, load_data, update_data, update_performance_metrics
from gpt4all_manager import initialize_gpt4all, generate_response
from log_manager import LogManager
import os
import json
from threading import Event
import numpy as np
from some_problem_solving_module import solve_astar, solve_dijkstra
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
import pickle

# Disable oneDNN custom operations to avoid numerical errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class BrainModel:
    def __init__(self):
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        self.models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
        self.logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        self.model_path = os.path.join(self.data_dir, 'brain_model.keras')
        self.data_path = os.path.join(self.data_dir, 'brain_data.json')
        self.dictionaries_path = os.path.join(self.data_dir, 'dictionaries')
        self.log_manager = LogManager()
        self.stop_training_event = Event()
        self.neuron_threshold = 0.7  # Threshold to add neurons

        # Load or initialize the model
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
        else:
            self.model = initialize_model()

        # Initialize or load data
        if not os.path.exists(self.data_path):
            initialize_data(self.data_path)
        else:
            self.load_learned_data()

        # Initialize GPT4All model
        self.chatbot = initialize_gpt4all(self.models_dir)

        # Load dictionaries
        self.dictionaries = self.load_dictionaries()
        self.integrate_dictionaries()

        # Initialize learning model
        self.learning_model = LogisticRegression()
        self.load_learning_model()

        # Initialize LSTM model
        self.lstm_model = self.initialize_lstm_model()
        self.load_lstm_model()

    def initialize_lstm_model(self):
        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(None, 1)))
        model.add(Dense(1))
        model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
        return model

    def train(self, inputs, outputs):
        self.stop_training_event.clear()
        for epoch in range(1, 101):  # Train for 100 epochs or until stopped
            if self.stop_training_event.is_set():
                print("Training stopped.")
                break
            history = self.model.fit(inputs, outputs, epochs=1, verbose=0)
            update_data(self.data_path, 'training', {'inputs': inputs.tolist(), 'outputs': outputs.tolist()})
            update_performance_metrics(self.data_path, history.history['accuracy'][0], history.history['loss'][0])
            self.log_manager.log(f"Epoch {epoch} - Accuracy: {history.history['accuracy'][0]}, Loss: {history.history['loss'][0]}")
            self.check_and_add_neurons(history.history['accuracy'][0])
            print(f"Epoch {epoch} completed.")

    def check_and_add_neurons(self, accuracy):
        if accuracy < self.neuron_threshold:
            self.model = add_neurons_to_model(self.model, 1)  # Add one neuron
            self.log_manager.log(f"Added one neuron due to low accuracy: {accuracy}", logger_name='neuron')

    def chat(self, message):
        if not self.chatbot:
            return "Chatbot is not available. Please check the initialization."
        
        response = generate_response(self.chatbot, message)
        self.log_manager.log(f"Chat input: {message} - Chat response: {response}")
        return response

    def make_decision(self, decision_input):
        decision_methods = {
            'astar': solve_astar,
            'dijkstra': solve_dijkstra
        }
        
        method = decision_input.get('method')
        if method in decision_methods:
            return decision_methods[method](decision_input)
        else:
            return {"status": "Unsupported decision method"}

    def learn(self, learning_input):
        try:
            X = np.array(learning_input['features'])
            y = np.array(learning_input['labels'])
            
            # Vérifiez si X est 1D et reformatez-le en conséquence
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            
            # Vérifiez si y est 1D et reformatez-le en conséquence
            if y.ndim == 1:
                y = y.reshape(-1, 1)
            
            # Vérifiez que les données ne sont pas vides
            if X.size == 0 or y.size == 0:
                raise ValueError("Les données d'apprentissage sont vides")
            
            self.learning_model.fit(X, y)
            accuracy = accuracy_score(y, self.learning_model.predict(X))
            self.save_learning_model()
            self.log_manager.log(f"Learning completed - Accuracy: {accuracy}")
            return {'status': 'Learning completed', 'accuracy': accuracy}
        except Exception as e:
            self.log_manager.log(f"Learning error: {str(e)}", level='error')
            return {'status': 'Error', 'message': str(e)}

    def recognize_pattern(self, pattern_input):
        try:
            X = np.array(pattern_input['features'])
            predictions = self.learning_model.predict(X)
            self.log_manager.log(f"Pattern recognition completed - Predictions: {predictions.tolist()}")
            return {'status': 'Pattern recognition completed', 'predictions': predictions.tolist()}
        except Exception as e:
            self.log_manager.log(f"Pattern recognition error: {str(e)}", level='error')
            return {'status': 'Error', 'message': str(e)}

    def train_lstm(self, series_data):
        try:
            X = np.array(series_data['features'])
            y = np.array(series_data['labels'])
            self.lstm_model.fit(X, y, epochs=50, verbose=0)
            self.save_lstm_model()
            self.log_manager.log("LSTM training completed")
            return {'status': 'LSTM training completed'}
        except Exception as e:
            self.log_manager.log(f"LSTM training error: {str(e)}", level='error')
            return {'status': 'Error', 'message': str(e)}

    def predict_lstm(self, input_data):
        try:
            X = np.array(input_data['features'])
            predictions = self.lstm_model.predict(X)
            self.log_manager.log(f"LSTM prediction completed - Predictions: {predictions.tolist()}")
            return {'status': 'LSTM prediction completed', 'predictions': predictions.tolist()}
        except Exception as e:
            self.log_manager.log(f"LSTM prediction error: {str(e)}", level='error')
            return {'status': 'Error', 'message': str(e)}

    def get_neuron_count(self):
        data = load_data(self.data_path)
        return len(data['neurons'])

    def get_function_count(self):
        data = load_data(self.data_path)
        return len(data['functions'])

    def load_dictionaries(self):
        dictionaries = {}
        if os.path.exists(self.dictionaries_path):
            for filename in os.listdir(self.dictionaries_path):
                if filename.endswith('.json'):
                    with open(os.path.join(self.dictionaries_path, filename), 'r', encoding='utf-8') as f:
                        dictionaries[filename] = json.load(f)
        return dictionaries

    def integrate_dictionaries(self):
        for dict_name, dictionary in self.dictionaries.items():
            for func_name, func_body in dictionary.items():
                if isinstance(func_body, str):
                    exec(f'def {func_name}(self): {func_body}')
                    setattr(self, func_name, locals()[func_name])

    def get_network_status(self):
        try:
            if self.model is None:
                return {'status': 'Offline', 'reason': 'Model not loaded'}

            try:
                dummy_input = np.array([[0.0, 0.0, 0.0]])
                prediction = self.model.predict(dummy_input)
                if prediction is not None:
                    return {'status': 'Operational', 'reason': None}
                else:
                    return {'status': 'Offline', 'reason': 'Model failed to make predictions'}
            except Exception as e:
                return {'status': 'Offline', 'reason': f'Model prediction error: {str(e)}'}
        except Exception as e:
            return {'status': 'Offline', 'reason': str(e)}

    def get_performance_metrics(self):
        data = load_data(self.data_path)
        return data.get('performance_metrics', {'accuracy': 0, 'loss': 0})

    def get_training_progress(self):
        data = load_data(self.data_path)
        epochs = range(1, len(data['training']) + 1)
        progress = [{'epoch': epoch, 'inputs': training['inputs'], 'outputs': training['outputs']} for epoch, training in zip(epochs, data['training'])]
        return progress

    def get_neural_connections(self):
        data = load_data(self.data_path)
        return data.get('connections', {'nodes': [], 'links': []})

    def get_neurons(self):
        data = load_data(self.data_path)
        return data.get('neurons', [])

    def update_neural_connection(self, source_id, target_id, weight):
        data = load_data(self.data_path)
        for link in data['connections']['links']:
            if link['source'] == source_id and link['target'] == target_id:
                link['value'] = weight
                break
        else:
            data['connections']['links'].append({'source': source_id, 'target': target_id, 'value': weight})
        with open(self.data_path, 'w') as f:
            json.dump(data, f)

    def stop_training(self):
        self.stop_training_event.set()

    def save_learning_model(self):
        learning_model_path = os.path.join(self.models_dir, 'learning_model.pkl')
        with open(learning_model_path, 'wb') as f:
            pickle.dump(self.learning_model, f)

    def load_learning_model(self):
        learning_model_path = os.path.join(self.models_dir, 'learning_model.pkl')
        if os.path.exists(learning_model_path):
            with open(learning_model_path, 'rb') as f:
                self.learning_model = pickle.load(f)

    def save_lstm_model(self):
        lstm_model_path = os.path.join(self.models_dir, 'lstm_model.h5')
        self.lstm_model.save(lstm_model_path)

    def load_lstm_model(self):
        lstm_model_path = os.path.join(self.models_dir, 'lstm_model.h5')
        if os.path.exists(lstm_model_path):
            self.lstm_model = tf.keras.models.load_model(lstm_model_path)

    def load_learned_data(self):
        data = load_data(self.data_path)
        # You can add more logic here if needed to load specific learned data

# Fin du fichier brain_model.py - Version 2.8

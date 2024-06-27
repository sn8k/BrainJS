# Emplacement: backend/data_manager.py
# Nom du fichier: data_manager.py
# Version: 1.0

import os
import json
import numpy as np
from json.decoder import JSONDecodeError

def initialize_data(data_path):
    data = {
        'neurons': [{'id': i, 'name': f'neuron{i}', 'state': np.random.rand()} for i in range(1, 101)],  # Initialisation de 100 neurones avec des états aléatoires
        'functions': [{'id': i, 'name': f'function{i}'} for i in range(1, 21)],  # Initialisation de 20 fonctions
        'training': [
            {
                'inputs': np.random.rand(10, 3).tolist(),  # 10 échantillons d'entrées aléatoires
                'outputs': np.random.randint(0, 2, size=(10, 1)).tolist()  # 10 échantillons de sorties binaires
            }
        ],
        'performance_metrics': {'accuracy': 0, 'loss': 0},
        'connections': {
            'nodes': [{'id': f'neuron{i}', 'group': 1} for i in range(1, 101)],
            'links': [{'source': f'neuron{i}', 'target': f'neuron{j}', 'value': np.random.rand()} for i in range(1, 100) for j in range(i+1, 101) if np.random.rand() > 0.7]  # Connexions aléatoires
        }
    }
    with open(data_path, 'w') as f:
        json.dump(data, f)

def load_data(data_path):
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except JSONDecodeError as e:
        print(f"Erreur de chargement du fichier JSON : {e}")
        return {}

def update_data(data_path, key, value):
    data = load_data(data_path)
    data[key].append(value)
    with open(data_path, 'w') as f:
        json.dump(data, f)

def update_performance_metrics(data_path, accuracy, loss):
    data = load_data(data_path)
    data['performance_metrics'] = {'accuracy': accuracy, 'loss': loss}
    with open(data_path, 'w') as f:
        json.dump(data, f)

# Fin du fichier data_manager.py - Version 1.0

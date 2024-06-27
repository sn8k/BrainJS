# gateway.py - Version 1.0
# Emplacement: backend/gateway.py

from data_manager import load_data, update_data
from model_utils import load_model, save_model

class Gateway:
    def __init__(self):
        self.data_dir = 'data'
        self.models_dir = 'models'
        self.logs_dir = 'logs'
        self.data_path = f'{self.data_dir}/brain_data.json'
        self.model_path = f'{self.models_dir}/brain_model.keras'
        self.data = self.load_data()
        self.model = self.load_model()

    def load_data(self):
        return load_data(self.data_path)

    def update_data(self, key, value):
        self.data[key] = value
        update_data(self.data_path, key, value)

    def load_model(self):
        return load_model(self.model_path)

    def save_model(self, model):
        save_model(self.model_path, model)

    def get_data(self, key):
        return self.data.get(key, None)

    def set_data(self, key, value):
        self.data[key] = value
        self.update_data(key, value)

# Fin du fichier gateway.py - Version 1.0

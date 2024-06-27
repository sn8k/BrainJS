# model_utils.py - Version 1.5
# Emplacement: backend/model_utils.py

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

def initialize_model():
    model = Sequential()
    model.add(Dense(64, input_dim=3, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def load_model(model_path):
    return tf.keras.models.load_model(model_path)

def save_model(model, model_path):
    model.save(model_path)

def add_neurons_to_model(model, num_neurons):
    new_model = Sequential()
    for layer in model.layers:
        if isinstance(layer, Dense):
            units = layer.units + num_neurons
            new_layer = Dense(units, activation=layer.activation)
            new_model.add(new_layer)
        else:
            new_model.add(layer)
    new_model.build(input_shape=model.input_shape)
    new_model.set_weights(model.get_weights())
    new_model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return new_model

# Fin du fichier model_utils.py - Version 1.5

# Emplacement: backend/gpt4all_manager.py
# Nom du fichier: gpt4all_manager.py
# Version: 2.3

import os
import json
import logging
from gpt4all import GPT4All

# Configurer la journalisation
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_gpt4all(model_directory):
    logging.info("Initialisation de GPT4All...")
    
    if not os.path.exists(model_directory):
        os.makedirs(model_directory)
        logging.info(f"Répertoire créé : {model_directory}")

    model_files = [f for f in os.listdir(model_directory) if f.endswith('.gguf') or f.endswith('.bin')]
    
    if not model_files:
        logging.error(f"Aucun fichier de modèle trouvé dans {model_directory}. Veuillez ajouter un fichier de modèle.")
        return None
    
    # Prioritize gguf files over bin files
    model_files.sort(key=lambda x: x.endswith('.gguf'), reverse=True)
    model_path = os.path.join(model_directory, model_files[0])

    logging.info(f"Utilisation du chemin de modèle : {model_path}")

    try:
        chatbot = GPT4All(model_path)
        logging.info("GPT4All initialisé avec succès.")
        return chatbot
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de GPT4All avec le modèle {model_path}: {e}")
        return None

def generate_response(chatbot, message):
    try:
        logging.info(f"Génération de réponse pour le message : {message}")
        response = chatbot.generate(message)
        
        # Print the type and content of the response for debugging
        logging.debug(f"Type de réponse : {type(response)}")
        logging.debug(f"Contenu de la réponse : {response}")

        # Ensure the response is a string
        if isinstance(response, str):
            generated_response = response
        else:
            logging.error("Format de réponse inattendu du chatbot.")
            return "Erreur : Format de réponse inattendu du chatbot."
        
        logging.info(f"Réponse générée : {generated_response}")
        return generated_response
    except Exception as e:
        logging.error(f"Erreur lors de la génération de la réponse : {e}")
        return "Erreur : Échec de la génération d'une réponse."

# Fin du fichier gpt4all_manager.py - Version 2.3

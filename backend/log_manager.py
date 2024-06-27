# log_manager.py - Version 1.2
# Emplacement: backend/log_manager.py

import os
import logging
from logging.handlers import RotatingFileHandler

class LogManager:
    def __init__(self):
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.main_log = self.setup_logger('main', os.path.join(self.log_dir, 'main.log'))
        self.brain_log = self.setup_logger('brain', os.path.join(self.log_dir, 'brain.log'))
        self.network_log = self.setup_logger('network', os.path.join(self.log_dir, 'network.log'))
        self.neuron_log = self.setup_logger('neuron', os.path.join(self.log_dir, 'neuron.log'))

    def setup_logger(self, name, log_file, level=logging.DEBUG):
        handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=3)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def log(self, message, logger_name='main'):
        logger = getattr(self, f"{logger_name}_log", self.main_log)
        logger.debug(message)

    def get_logs(self):
        logs = {}
        for log_file in ['main.log', 'brain.log', 'network.log', 'neuron.log']:
            log_path = os.path.join(self.log_dir, log_file)
            with open(log_path, 'r') as file:
                logs[log_file] = file.read()
        return logs

# Fin du fichier log_manager.py - Version 1.2

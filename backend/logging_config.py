# logging_config.py - Version 1.1
# Emplacement: backend/logging_config.py

import logging
import logging.config
import os

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))

def setup_logging():
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'file_main': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(log_dir, 'main.log'),
            },
            'file_brain': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(log_dir, 'brain.log'),
            },
            'file_network': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(log_dir, 'network.log'),
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file_main'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'brain': {
                'handlers': ['file_brain'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'network': {
                'handlers': ['file_network'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

# Fin du fichier logging_config.py - Version 1.1

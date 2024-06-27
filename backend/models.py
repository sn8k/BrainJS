# models.py - Version 1.2
# Emplacement: backend/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    hostname = db.Column(db.String(100))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True)

class NeuralData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(50))
    data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Text)

class TrainingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True)

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True)

class NetworkScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    hostname = db.Column(db.String(100))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True)
    
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Fin du fichier models.py - Version 1.2

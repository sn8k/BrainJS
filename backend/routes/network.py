# network.py - Version 1.8
# Emplacement: backend/routes/network.py

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, request
from backend.models import ScanResult, db
from backend.network_scanner import NetworkScanner
import threading
import logging

# Création du blueprint pour les routes réseau
network_bp = Blueprint('network', __name__)
scan_active = False
scanner = NetworkScanner()
scan_progress = {'progress': 0, 'total': 1}

# Utilisation d'un logger spécifique pour le module réseau
logger = logging.getLogger('network')

@network_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Route principale pour afficher l'interface de scan réseau.
    """
    global scan_active
    # Récupération des résultats de scan depuis la base de données
    scan_results = ScanResult.query.order_by(ScanResult.timestamp.desc()).all()
    # Récupération des interfaces réseau disponibles
    interfaces = scanner.get_interfaces()
    # Rendu de la template avec les résultats de scan et les interfaces
    return render_template('network.html', scan_active=scan_active, scan_results=scan_results, interfaces=interfaces)

@network_bp.route('/toggle_scan', methods=['POST'])
def toggle_scan():
    """
    Route pour activer ou désactiver le scan réseau.
    """
    global scan_active
    scan_active = not scan_active
    ip_range = request.form.get('ip_range')

    if scan_active:
        flash("Le scan réseau a été activé.", "success")
        logger.debug("Activation du scan réseau")
        # Démarrage du scan réseau dans un thread séparé
        thread = threading.Thread(target=run_scan_with_progress, args=(current_app._get_current_object(), ip_range))
        thread.start()
    else:
        flash("Le scan réseau a été désactivé.", "success")
        logger.debug("Désactivation du scan réseau")
    return redirect(url_for('network.index'))

@network_bp.route('/start_scan', methods=['POST'])
def start_scan():
    """
    Route pour démarrer un scan réseau spécifique.
    """
    ip_range = request.form.get('ip_range')
    ip_ranges = [ip_range] if ip_range != "all" else scanner.get_ip_ranges()
    scan_progress['total'] = len(ip_ranges)
    scan_progress['progress'] = 0

    def scan():
        for ip_range in ip_ranges:
            scan_data = scanner.scan_network(ip_range)
            scanner.process_scan_data(scan_data)
            scan_progress['progress'] += 1

    scan_thread = threading.Thread(target=scan)
    scan_thread.start()
    return jsonify({'status': 'Scan started'})

@network_bp.route('/scan_progress', methods=['GET'])
def get_scan_progress():
    """
    Route pour obtenir la progression du scan réseau.
    """
    progress = (scan_progress['progress'] / scan_progress['total']) * 100
    return jsonify({'progress': progress})

@network_bp.route('/get_scan_results', methods=['GET'])
def get_scan_results():
    """
    Route pour récupérer les résultats des scans réseau.
    """
    scan_results = ScanResult.query.order_by(ScanResult.timestamp.desc()).all()
    results = []
    for result in scan_results:
        results.append({
            'timestamp': result.timestamp,
            'ip_address': result.ip_address,
            'status': result.status,
            'details': result.details
        })
    return jsonify({'scan_results': results})

def run_scan_with_progress(app, ip_range):
    """
    Fonction pour exécuter le scan réseau avec suivi de progression.
    """
    with app.app_context():
        ip_ranges = [ip_range] if ip_range != "all" else scanner.get_ip_ranges()
        scan_progress['total'] = len(ip_ranges)
        scan_progress['progress'] = 0

        for ip_range in ip_ranges:
            scan_data = scanner.scan_network(ip_range)
            scanner.process_scan_data(scan_data)
            scan_progress['progress'] += 1

# Fin du fichier network.py - Version 1.8

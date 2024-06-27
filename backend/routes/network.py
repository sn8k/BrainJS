# network.py - Version 1.8
# Emplacement: backend/routes/network.py

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, request
from backend.models import ScanResult, db
from backend.network_scanner import NetworkScanner
import threading
import logging

network_bp = Blueprint('network', __name__)
scan_active = False
scanner = NetworkScanner()
scan_progress = {'progress': 0, 'total': 1}

# Utiliser le logger spécifique pour le réseau
logger = logging.getLogger('network')

@network_bp.route('/', methods=['GET', 'POST'])
def index():
    global scan_active
    scan_results = ScanResult.query.order_by(ScanResult.timestamp.desc()).all()
    interfaces = scanner.get_interfaces()
    return render_template('network.html', scan_active=scan_active, scan_results=scan_results, interfaces=interfaces)

@network_bp.route('/toggle_scan', methods=['POST'])
def toggle_scan():
    global scan_active
    scan_active = not scan_active
    ip_range = request.form.get('ip_range')

    if scan_active:
        flash("Le scan réseau a été activé.", "success")
        logger.debug("Activation du scan réseau")
        thread = threading.Thread(target=run_scan_with_progress, args=(current_app._get_current_object(), ip_range))
        thread.start()
    else:
        flash("Le scan réseau a été désactivé.", "success")
        logger.debug("Désactivation du scan réseau")
    return redirect(url_for('network.index'))

@network_bp.route('/start_scan', methods=['POST'])
def start_scan():
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
    progress = (scan_progress['progress'] / scan_progress['total']) * 100
    return jsonify({'progress': progress})

@network_bp.route('/get_scan_results', methods=['GET'])
def get_scan_results():
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
    with app.app_context():
        ip_ranges = [ip_range] if ip_range != "all" else scanner.get_ip_ranges()
        scan_progress['total'] = len(ip_ranges)
        scan_progress['progress'] = 0

        for ip_range in ip_ranges:
            scan_data = scanner.scan_network(ip_range)
            scanner.process_scan_data(scan_data)
            scan_progress['progress'] += 1

# Fin du fichier network.py - Version 1.8

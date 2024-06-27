import nmap
import json
import logging
import socket
import struct
from backend.brain_model import BrainModel
import psutil  # Nouvelle importation pour obtenir les interfaces réseau

class NetworkScanner:
    def __init__(self):
        self.scanner = nmap.PortScanner()
        self.brain = BrainModel()
        self.logger = logging.getLogger('network_scanner')
        handler = logging.FileHandler('logs/network_scanner.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def get_ip_ranges(self):
        ip_ranges = []
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        subnet = self.get_subnet(ip_address, 24)
        ip_ranges.append(subnet)
        return ip_ranges

    def get_subnet(self, ip, prefix_length):
        ip_parts = ip.split('.')
        subnet = '.'.join(ip_parts[:3]) + '.0/' + str(prefix_length)
        return subnet

    def get_interfaces(self):
        interfaces = psutil.net_if_addrs()
        ip_ranges = []
        for interface_name, interface_addresses in interfaces.items():
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    subnet = self.get_subnet(address.address, 24)
                    ip_ranges.append({
                        'interface': interface_name,
                        'ip': address.address,
                        'subnet': subnet,
                        'netmask': address.netmask
                    })
        return ip_ranges

    def scan_network(self, target):
        self.logger.debug(f"Scanning network for target: {target}")
        self.scanner.scan(hosts=target, arguments='-sP -unprivileged')
        scan_data = []
        for host in self.scanner.all_hosts():
            host_data = {
                'host': host,
                'state': self.scanner[host].state(),
                'addresses': self.scanner[host].get('addresses', {}),
                'hostnames': self.scanner[host].get('hostnames', []),
                'vendor': self.scanner[host].get('vendor', {})
            }
            scan_data.append(host_data)
        self.logger.debug(f"Scan data collected: {scan_data}")
        return scan_data

    def process_scan_data(self, scan_data):
        self.logger.debug(f"Processing scan data: {scan_data}")
        features = self.extract_features(scan_data)
        labels = self.generate_labels(features)
        self.logger.debug(f"Features extracted: {features}")
        self.logger.debug(f"Labels generated: {labels}")

        if features and len(set(labels)) > 1:  # Ensure at least two classes are present
            self.brain.learn({'features': features, 'labels': labels})
        else:
            self.logger.error("No data to learn from. Features or labels are empty or contain only one class.")

    def extract_features(self, scan_data):
        features = []
        for data in scan_data:
            feature = [
                1 if data['state'] == 'up' else 0,
                len(data['addresses']),
                len(data['hostnames']),
                len(data['vendor']),
                # Ajout de nouvelles caractéristiques
                len(self.scanner[data['host']].all_tcp()),  # Nombre de ports TCP ouverts
                len(self.scanner[data['host']].all_udp())   # Nombre de ports UDP ouverts
            ]
            features.append(feature)
        self.logger.debug(f"Features: {features}")
        return features

    def generate_labels(self, features):
        # Exemple de condition pour introduire plus de diversité
        labels = [1 if feature[0] == 1 and feature[3] > 0 else 0 for feature in features]
        self.logger.debug(f"Labels: {labels}")
        return labels

# Fin du fichier network_scanner.py - Version 1.7

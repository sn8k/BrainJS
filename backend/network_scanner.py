# network_scanner.py - Version 1.8
# Emplacement: backend/network_scanner.py

import scapy.all as scapy
import logging
import socket
import psutil  # Pour obtenir les interfaces réseau
from backend.brain_model import BrainModel

class NetworkScanner:
    def __init__(self):
        # Initialisation du modèle de cerveau
        self.brain = BrainModel()

        # Configuration du logger pour le scanner réseau
        self.logger = logging.getLogger('network_scanner')
        handler = logging.FileHandler('logs/network_scanner.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def get_ip_ranges(self):
        """
        Obtenir les plages IP disponibles à partir de l'hôte actuel.
        """
        ip_ranges = []
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        subnet = self.get_subnet(ip_address, 24)
        ip_ranges.append(subnet)
        return ip_ranges

    def get_subnet(self, ip, prefix_length):
        """
        Obtenir la sous-réseau à partir d'une adresse IP et d'un préfixe de longueur.
        """
        ip_parts = ip.split('.')
        subnet = '.'.join(ip_parts[:3]) + '.0/' + str(prefix_length)
        return subnet

    def get_interfaces(self):
        """
        Obtenir les interfaces réseau disponibles sur l'hôte.
        """
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
        """
        Scanner le réseau pour une cible spécifique.
        """
        self.logger.debug(f"Scanning network for target: {target}")
        arp_request = scapy.ARP(pdst=target)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        scan_data = []
        for element in answered_list:
            host_data = {
                'host': element[1].psrc,
                'state': 'up',
                'addresses': {'ipv4': element[1].psrc},
                'hostnames': [{'name': element[1].hwsrc, 'type': ''}],
                'vendor': {}
            }
            scan_data.append(host_data)
        self.logger.debug(f"Scan data collected: {scan_data}")
        return scan_data

    def process_scan_data(self, scan_data):
        """
        Traiter les données de scan pour l'apprentissage du modèle.
        """
        self.logger.debug(f"Processing scan data: {scan_data}")
        features = self.extract_features(scan_data)
        labels = self.generate_labels(features)
        self.logger.debug(f"Features extracted: {features}")
        self.logger.debug(f"Labels generated: {labels}")

        if features and len(set(labels)) > 1:  # S'assurer qu'au moins deux classes sont présentes
            self.brain.learn({'features': features, 'labels': labels})
        else:
            self.logger.error("No data to learn from. Features or labels are empty or contain only one class.")

    def extract_features(self, scan_data):
        """
        Extraire les caractéristiques des données de scan.
        """
        features = []
        for data in scan_data:
            feature = [
                1 if data['state'] == 'up' else 0,
                len(data['addresses']),
                len(data['hostnames']),
                len(data['vendor']),
                1 if 'ipv4' in data['addresses'] else 0,  # Présence d'une adresse IPv4
                1 if 'ipv6' in data['addresses'] else 0,  # Présence d'une adresse IPv6
            ]
            features.append(feature)
        self.logger.debug(f"Features: {features}")
        return features

    def generate_labels(self, features):
        """
        Générer les étiquettes pour l'apprentissage à partir des caractéristiques.
        """
        labels = [1 if feature[0] == 1 and feature[1] > 0 else 0 for feature in features]
        self.logger.debug(f"Labels: {labels}")
        return labels

# Fin du fichier network_scanner.py - Version 1.8

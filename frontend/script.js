// script.js - Version 1.5
// Emplacement: frontend/static/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Gestionnaires d'événements pour les boutons
    document.getElementById('add-neuron-btn').addEventListener('click', addNeuron);
    document.getElementById('train-brain-btn').addEventListener('click', trainBrain);
    document.getElementById('chat-btn').addEventListener('click', chatWithBrain);
    document.getElementById('start-scan-btn').addEventListener('click', startScan);

    // Gestionnaires d'événements pour les formulaires de paramètres
    document.getElementById('general-settings-form').addEventListener('submit', saveGeneralSettings);
    document.getElementById('training-settings-form').addEventListener('submit', saveTrainingSettings);
    document.getElementById('logging-settings-form').addEventListener('submit', saveLoggingSettings);
    document.getElementById('view-logs-form').addEventListener('submit', viewLogFile);
    document.getElementById('monitoring-settings-form').addEventListener('submit', saveMonitoringSettings);

    // Fonction pour ajouter un neurone
    function addNeuron() {
        const neuronId = prompt("Enter neuron ID:");
        fetch('/add_neuron', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ neuron_id: neuronId })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Neuron added:', data);
            alert('Neuron added successfully!');
            updateStats();
        })
        .catch(error => {
            console.error('Error adding neuron:', error);
            alert('Error adding neuron');
        });
    }

    // Fonction pour entraîner le réseau neuronal
    function trainBrain() {
        const inputs = prompt("Enter inputs (as JSON array):");
        const outputs = prompt("Enter outputs (as JSON array):");
        fetch('/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ inputs: JSON.parse(inputs), outputs: JSON.parse(outputs) })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Training completed:', data);
            alert('Training completed successfully!');
            updateStats();
        })
        .catch(error => {
            console.error('Error training brain:', error);
            alert('Error training brain');
        });
    }

    // Fonction pour dialoguer avec le réseau neuronal
    function chatWithBrain() {
        const message = prompt("Enter your message:");
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Chat response:', data);
            alert('Brain response: ' + data.response);
        })
        .catch(error => {
            console.error('Error chatting with brain:', error);
            alert('Error chatting with brain');
        });
    }

    // Fonction pour sauvegarder les paramètres généraux
    function saveGeneralSettings(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        fetch('/settings/general', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(data)),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('General settings saved:', data);
            alert('General settings saved successfully!');
        })
        .catch(error => {
            console.error('Error saving general settings:', error);
            alert('Error saving general settings');
        });
    }

    // Fonction pour sauvegarder les paramètres d'entraînement
    function saveTrainingSettings(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        fetch('/settings/training', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(data)),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Training settings saved:', data);
            alert('Training settings saved successfully!');
        })
        .catch(error => {
            console.error('Error saving training settings:', error);
            alert('Error saving training settings');
        });
    }

    // Fonction pour sauvegarder les paramètres de journalisation
    function saveLoggingSettings(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        fetch('/settings/logging', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(data)),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Logging settings saved:', data);
            alert('Logging settings saved successfully!');
        })
        .catch(error => {
            console.error('Error saving logging settings:', error);
            alert('Error saving logging settings');
        });
    }

    // Fonction pour afficher le contenu d'un fichier journal
    function viewLogFile(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        fetch(`/logs?file=${data.get('log_file')}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById('log-content').textContent = data;
        })
        .catch(error => {
            console.error('Error fetching log file:', error);
            alert('Error fetching log file');
        });
    }

    // Fonction pour sauvegarder les paramètres de surveillance
    function saveMonitoringSettings(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        fetch('/settings/monitoring', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(data)),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Monitoring settings saved:', data);
            alert('Monitoring settings saved successfully!');
        })
        .catch(error => {
            console.error('Error saving monitoring settings:', error);
            alert('Error saving monitoring settings');
        });
    }

    // Fonction pour vérifier le statut du réseau neuronal
    function checkNetworkStatus() {
        fetch('/network-status')
        .then(response => response.json())
        .then(data => {
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const statusReason = document.getElementById('status-reason');
            if (data.status === 'OK') {
                statusIndicator.classList.remove('badge-danger');
                statusIndicator.classList.add('badge-success');
                statusText.textContent = 'OK';
                statusReason.textContent = '';
            } else {
                statusIndicator.classList.remove('badge-success');
                statusIndicator.classList.add('badge-danger');
                statusText.textContent = 'KO';
                statusReason.textContent = `Reason: ${data.reason}`;
            }
        })
        .catch(error => {
            console.error('Error checking network status:', error);
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const statusReason = document.getElementById('status-reason');
            statusIndicator.classList.remove('badge-success');
            statusIndicator.classList.add('badge-danger');
            statusText.textContent = 'KO';
            statusReason.textContent = 'Error checking network status';
        });
    }

    // Fonction pour mettre à jour les statistiques
    function updateStats() {
        fetch('/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('neurons-count').textContent = data.neurons;
            document.getElementById('functions-learned-count').textContent = data.functions_learned;
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            alert('Error fetching stats');
        });
    }

    // Récupérer les statistiques et le statut du réseau au chargement de la page
    updateStats();
    checkNetworkStatus();

    // Optionnel : Vérifiez régulièrement le statut du réseau (par exemple, toutes les 30 secondes)
    setInterval(checkNetworkStatus, 30000);

    // Ajout des nouvelles fonctionnalités pour la page Cognition & Decision

    // Fonction pour soumettre des données de décision
    function submitDecision() {
        const decisionInput = document.getElementById('decisionInput').value;
        fetch('/cognition_decision/make_decision', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: decisionInput })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('decisionResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error making decision:', error);
            alert('Error making decision');
        });
    }

    // Fonction pour soumettre des données de résolution de problème
    function submitProblem() {
        const problemInput = document.getElementById('problemInput').value;
        fetch('/cognition_decision/solve_problem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: problemInput })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('problemResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error solving problem:', error);
            alert('Error solving problem');
        });
    }

    // Fonction pour soumettre des données d'apprentissage
    function submitLearning() {
        const learningInput = document.getElementById('learningInput').value;
        fetch('/cognition_decision/learn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: JSON.parse(learningInput) })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('learningResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error learning:', error);
            alert('Error learning');
        });
    }

    // Fonction pour soumettre des données de reconnaissance de motifs
    function submitPattern() {
        const patternInput = document.getElementById('patternInput').value;
        fetch('/cognition_decision/recognize_pattern', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: JSON.parse(patternInput) })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('patternResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error recognizing pattern:', error);
            alert('Error recognizing pattern');
        });
    }

    // Fonction pour soumettre des données d'entraînement LSTM
    function trainLSTM() {
        const trainLSTMInput = document.getElementById('trainLSTMInput').value;
        fetch('/cognition_decision/train_lstm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: JSON.parse(trainLSTMInput) })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('trainLSTMResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error training LSTM:', error);
            alert('Error training LSTM');
        });
    }

    // Fonction pour soumettre des données de prédiction LSTM
    function predictLSTM() {
        const predictLSTMInput = document.getElementById('predictLSTMInput').value;
        fetch('/cognition_decision/predict_lstm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: JSON.parse(predictLSTMInput) })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('predictLSTMResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error predicting LSTM:', error);
            alert('Error predicting LSTM');
        });
    }

    // Fonction pour démarrer le scan
    function startScan() {
        fetch('/network/start_scan', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Scan started:', data);
            updateProgress();
        })
        .catch(error => {
            console.error('Error starting scan:', error);
            alert('Error starting scan');
        });
    }

    // Fonction pour mettre à jour la progression du scan
    function updateProgress() {
        fetch('/network/scan_progress')
        .then(response => response.json())
        .then(data => {
            document.getElementById('scan-progress-bar').value = data.progress;
            if (data.progress < 100) {
                setTimeout(updateProgress, 1000);
            } else {
                alert('Scan completed');
            }
        })
        .catch(error => {
            console.error('Error getting scan progress:', error);
            alert('Error getting scan progress');
        });
    }
});

// Fin du fichier script.js - Version 1.5

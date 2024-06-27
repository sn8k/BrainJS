# emotions_social.py - Version 1.5
# Emplacement: backend/routes/emotions_social.py

from flask import Blueprint, render_template, request, jsonify
from backend.brain_model import BrainModel
from backend.models import NeuralData, db
import discord
import asyncio
import os
import json
from datetime import datetime

emotions_social_bp = Blueprint('emotions_social', __name__)
brain = BrainModel()

config_path = os.path.join(os.getcwd(), 'data', 'config.json')

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

config = load_config()

# Discord bot configuration
intents = discord.Intents.default()
client = discord.Client(intents=intents)
DISCORD_TOKEN = config.get('discord_token', '')
DISCORD_CHANNEL_ID = config.get('discord_channel_id', '')

if DISCORD_CHANNEL_ID:
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)

async def send_discord_message(message):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    await channel.send(message)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Flask routes
@emotions_social_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.json['message']
        response = brain.chat(message)

        neural_data = NeuralData(data_type='chat', data=json.dumps({'message': message, 'response': response}), timestamp=datetime.utcnow())
        db.session.add(neural_data)
        db.session.commit()

        return jsonify({'response': response})
    return render_template('emotions_social.html')

@emotions_social_bp.route('/discord', methods=['POST'])
def discord_message():
    message = request.json['message']
    asyncio.run(send_discord_message(message))

    neural_data = NeuralData(data_type='discord_message', data=json.dumps({'message': message}), timestamp=datetime.utcnow())
    db.session.add(neural_data)
    db.session.commit()

    return jsonify({'response': 'Message sent to Discord'})

# Start the Discord bot
if DISCORD_TOKEN and DISCORD_CHANNEL_ID:
    client.run(DISCORD_TOKEN)

# Fin du fichier emotions_social.py - Version 1.5

# view.py - Version 3.0
# Emplacement: backend/routes/view.py

from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
import cv2
import os
from threading import Thread
import random
import json
import asyncio
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio
import requests

nest_asyncio.apply()

view_bp = Blueprint('view', __name__)

camera = None
config_path = os.path.join(os.getcwd(), 'data', 'config.json')

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            if "video_sources" not in config:
                config["video_sources"] = ["https://www.earthcam.com/"]
            if "selected_source" not in config:
                config["selected_source"] = config["video_sources"][0]
            if "chromium_path" not in config:
                config["chromium_path"] = ""
            if "auto_learn" not in config:
                config["auto_learn"] = False
            return config
    else:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)  # Ensure the directory exists
        return {
            "auto_learn": False,
            "video_sources": ["https://www.earthcam.com/"],
            "selected_source": "https://www.earthcam.com/",
            "chromium_path": "",
            "verbosity_level": "INFO",
            "neural_network_status": "active",
            "training_epochs": 10
        }

def save_config(config):
    with open(config_path, 'w') as f:
        json.dump(config, f)

config = load_config()

def capture_frames(device_index):
    global camera
    camera = cv2.VideoCapture(device_index)
    while True:
        ret, frame = camera.read()
        if ret:
            # Afficher le cadre capturé
            cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()

def auto_learn_from_camera():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    while config.get("auto_learn", False):
        camera_url = loop.run_until_complete(get_random_camera_url())
        if camera_url:
            stream_video(camera_url)

class CameraCrawler:
    def __init__(self, sources, max_threads=10):
        self.sources = sources
        self.max_threads = max_threads
        self.cameras = []

    def fetch_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.parse_html(response.text, url)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    def parse_html(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        if "insecam.org" in url:
            for a in soup.find_all('a', href=True):
                if '/camera/view/' in a['href']:
                    camera_url = "http://www.insecam.org" + a['href']
                    if camera_url not in self.cameras:
                        self.cameras.append(camera_url)
        elif "earthcam.com" in url:
            for script in soup.find_all('script'):
                if script.string and 'var camVideo =' in script.string:
                    start = script.string.find("https://")
                    end = script.string.find(".mp4") + 4
                    cam_url = script.string[start:end]
                    if cam_url and cam_url not in self.cameras:
                        self.cameras.append(cam_url)

    def crawl(self):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(self.fetch_url, self.sources)
        return self.cameras

async def get_random_camera_url():
    crawler = CameraCrawler(config["video_sources"])
    cameras = crawler.crawl()
    if cameras:
        return random.choice(cameras)
    return None

def stream_video(camera_url):
    cap = cv2.VideoCapture(camera_url)
    while config.get("auto_learn", False):
        ret, frame = cap.read()
        if ret:
            # Afficher le cadre de streaming
            cv2.imshow('Auto Learning Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

@view_bp.route('/', methods=['GET', 'POST'])
def index():
    global config
    if request.method == 'POST':
        if 'video_url' in request.form:
            video_url = request.form['video_url']
            if video_url and video_url not in config["video_sources"]:
                config["video_sources"].append(video_url)
                save_config(config)
                flash('Video source added successfully!', 'success')
        if 'start_webcam' in request.form:
            device_index = request.form.get('device_index', 0)
            thread = Thread(target=capture_frames, args=(int(device_index),))
            thread.start()
        if 'auto_learn' in request.form:
            config["auto_learn"] = not config.get("auto_learn", False)
            save_config(config)
            if config["auto_learn"]:
                thread = Thread(target=auto_learn_from_camera)
                thread.start()
        if 'selected_source' in request.form:
            config["selected_source"] = request.form['selected_source']
            save_config(config)
    return render_template('view.html', auto_learn=config.get("auto_learn", False), video_sources=config.get("video_sources"), selected_source=config.get("selected_source"))

@view_bp.route('/stop_webcam', methods=['POST'])
def stop_webcam():
    global camera
    if camera:
        camera.release()
    cv2.destroyAllWindows()
    return redirect(url_for('view.index'))

def generate_frames():
    global camera
    while True:
        if camera is not None:
            ret, frame = camera.read()
            if not ret:
                break
            else:
                # Ajouter un cadrillage en overlay
                height, width = frame.shape[:2]
                for i in range(0, width, 50):
                    cv2.line(frame, (i, 0), (i, height), (255, 0, 0), 1)
                for j in range(0, height, 50):
                    cv2.line(frame, (0, j), (width, j), (255, 0, 0), 1)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@view_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Fin du fichier view.py - Version 3.0

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import json
import time
import threading
import subprocess
import sys
from scan import process

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['UPLOAD_FOLDER'] = './temp'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB limit
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov'}

# Use relative paths for deployment compatibility
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'weights')
CFG_FILE = os.path.join(os.path.dirname(__file__), 'config.json') 
DEVICE = os.environ.get('DEVICE', 'cpu')

# Ensure temp directory exists
os.makedirs('temp', exist_ok=True)

# Global variable to track if model is ready
MODEL_READY = False
MODEL_ERROR = None

# Function to start the model initialization in a separate process
def start_model_initialization():
    print("Starting model worker process...")
    try:
        # Run the model_worker.py script as a separate process
        subprocess.Popen([sys.executable, "model_worker.py"])
    except Exception as e:
        print(f"Error starting model worker: {e}")
        global MODEL_ERROR
        MODEL_ERROR = str(e)

# Start model initialization in the background
threading.Thread(target=start_model_initialization).start()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'message': 'DeepFake Detection API is running. Use the /detect endpoint with a POST request to analyze a video.'
    })

@app.route('/status', methods=['GET'])
def model_status():
    """Check if the model is ready for inference"""
    if os.path.exists("model_ready.json"):
        try:
            with open("model_ready.json", "r") as f:
                status = json.load(f)
                if status["status"] == "ready":
                    return jsonify({
                        "status": "ready",
                        "message": "Model is ready for inference",
                        "initialization_time": status.get("initialization_time", 0)
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Model initialization failed",
                        "error": status.get("error", "Unknown error")
                    }), 500
        except Exception as e:
            return jsonify({
                "status": "initializing",
                "message": "Checking model status failed",
                "error": str(e)
            }), 500
    else:
        return jsonify({
            "status": "initializing",
            "message": "Model is still initializing, please check back later"
        }), 202  # 202 Accepted means the request was accepted but processing is not complete

@app.route('/detect', methods=['POST'])
def detect_deepfake():
    # Check if model is ready
    if not os.path.exists("model_ready.json"):
        return jsonify({
            'error': 'Model is still initializing. Please try again later or check /status endpoint.',
            'status': 'initializing'
        }), 503  # Service Unavailable
    
    try:
        with open("model_ready.json", "r") as f:
            status = json.load(f)
            if status["status"] != "ready":
                return jsonify({
                    'error': 'Model initialization failed',
                    'status': 'error',
                    'details': status.get("error", "Unknown error")
                }), 500
    except Exception as e:
        return jsonify({'error': f'Failed to check model status: {str(e)}'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save the file temporarily
    temp_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    file.save(save_path)
    
    try:
        score = process(save_path)
        # Ensure score is a Python float
        score = float(score)
        # Convert NumPy boolean to Python boolean
        is_deepfake = bool(score > 0.5)
        os.remove(save_path)
        return jsonify({
            'score': score,
            'is_deepfake': is_deepfake  # Now a Python boolean
        })
    except Exception as e:
        os.remove(save_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("Starting DeepFake Detection API server")
    print("You can use this API to detect DeepFake videos")
    print("Use the /detect endpoint with a POST request and a video file")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
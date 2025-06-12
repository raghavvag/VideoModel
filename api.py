from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from scan import init, process
from model_download import download_models

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['UPLOAD_FOLDER'] = './temp'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB limit
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov'}

# Initialize the model once at startup
# Use relative paths for deployment compatibility
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'weights')
CFG_FILE = os.path.join(os.path.dirname(__file__), 'config.json') 
DEVICE = os.environ.get('DEVICE', 'cpu')  # Use environment variable or default to CPU

# Ensure all required directories exist
os.makedirs('temp', exist_ok=True)
os.makedirs('weights', exist_ok=True)
os.makedirs(os.path.dirname(CFG_FILE), exist_ok=True)

# Download models if needed (for cloud deployment)
if os.environ.get('DOWNLOAD_MODELS', 'False').lower() == 'true':
    download_models()

init(MODELS_DIR, CFG_FILE, DEVICE)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'message': 'DeepFake Detection API is running. Use the /detect endpoint with a POST request to analyze a video.'
    })

@app.route('/detect', methods=['POST'])
def detect_deepfake():
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
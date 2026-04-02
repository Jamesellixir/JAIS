import os
import secrets
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from router import analyze_and_route

app = Flask(__name__)
# Generate a secret key for session management (if needed later)
app.secret_key = secrets.token_hex(16)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the GUI and route them."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    
    try:
        # Route the request using our existing logic
        result = analyze_and_route(user_message)
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads from the GUI."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            return jsonify({
                'message': f'File {filename} successfully uploaded.',
                'filepath': filepath
            })
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """Returns a list of files in the current workspace directory."""
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # Avoid showing internal/hidden directories like __pycache__ or uploads
        files = []
        for f in os.listdir(workspace_dir):
            if os.path.isfile(os.path.join(workspace_dir, f)) and not f.startswith('.'):
                files.append(f)
        return jsonify({'files': sorted(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<path:filename>', methods=['GET'])
def get_file_content(filename):
    """Returns the text content of a specific file."""
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(workspace_dir, filename)
    
    # Security: Ensure we don't read outside the workspace
    if not os.path.abspath(filepath).startswith(workspace_dir):
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    except UnicodeDecodeError:
        return jsonify({'error': 'File is binary or not readable as text'})
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Run the server on available port
    app.run(host='127.0.0.1', port=5000, debug=True)

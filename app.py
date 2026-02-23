import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 1. Serve the UI Dashboard
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 2. Serve the Thumbnail Images from .cache
@app.route('/cache/<path:filename>')
def serve_cache(filename):
    return send_from_directory('.cache', filename)

# 3. Serve the Match Data
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # We will load the full report so you can see ALL faces, 
        # even if they didn't have a match in groups.json yet.
        with open('report.json', 'r') as f:
            data = json.load(f)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. The Windows Native Folder Execution
@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    data = request.json
    folder_path = data.get('path')
    
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Invalid path"}), 400
        
    try:
        os.startfile(folder_path) 
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(">>> Visage Server Online: http://localhost:5000")
    app.run(port=5000, debug=True)
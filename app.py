import os
import json
import subprocess
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Import your actual engines
from extractor import scan_directory
from matcher import build_clusters

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index(): return send_from_directory('.', 'index.html')

@app.route('/cache/<path:filename>')
def serve_cache(filename): return send_from_directory('.cache', filename)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        with open('report.json', 'r') as f: return jsonify({"status": "success", "data": json.load(f)})
    except: return jsonify({"status": "success", "data": {}})

@app.route('/api/groups', methods=['GET'])
def get_groups():
    try:
        if not os.path.exists('groups.json'): return jsonify({"status": "success", "data": []})
        with open('groups.json', 'r') as f: return jsonify({"status": "success", "data": json.load(f)})
    except: return jsonify({"status": "success", "data": []})

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    path = request.json.get('path')
    if path and os.path.exists(path):
        # Force Windows to open the explorer process directly
        # os.path.normpath fixes any weird slash directions
        clean_path = os.path.normpath(path)
        subprocess.Popen(['explorer', clean_path])
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid path"}), 400

# NEW: The Scanner API
@app.route('/api/scan', methods=['POST'])
def run_scan():
    folder_path = request.json.get('path')
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Path does not exist."}), 400
        
    try:
        print(f"\n>>> UI TRIGGERED SCAN: {folder_path}")
        # 1. Extract the faces
        scan_directory(folder_path)
        # 2. Immediately rebuild the clusters so the UI has fresh data
        build_clusters()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(">>> Visage Server Online: http://localhost:5000")
    app.run(port=5000, debug=True)
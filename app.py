import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your vanilla JS frontend to talk to this backend

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "Visage Engine Online", "version": "1.0.0"})

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """Receives a path from the frontend and opens it natively in Windows."""
    data = request.json
    folder_path = data.get('path')
    
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Invalid or missing path"}), 400
        
    try:
        # The Windows magic command
        os.startfile(folder_path) 
        return jsonify({"status": "success", "message": f"Opened {folder_path}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(">>> Visage Backend Initializing...")
    print(">>> Listening on http://localhost:5000")
    app.run(port=5000, debug=True)
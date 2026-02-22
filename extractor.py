import os
import cv2
import face_recognition
import json
from pathlib import Path

# Setup our paths
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True) # Creates the hidden folder if it doesn't exist
REPORT_FILE = "report.json"

def get_face_from_image(image_path, folder_id):
    """Loads an image, finds a face, crops it, and saves it to .cache"""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        return None # No face found, move on

    # Grab the first face found [top, right, bottom, left]
    top, right, bottom, left = face_locations[0]
    
    # Read with OpenCV to crop and save (OpenCV uses BGR, face_recognition uses RGB)
    cv_image = cv2.imread(image_path)
    face_crop = cv_image[top:bottom, left:right]
    
    cache_path = CACHE_DIR / f"{folder_id}.jpg"
    cv2.imwrite(str(cache_path), face_crop)
    
    # Get the mathematical encoding of the face for later comparison
    encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
    return str(cache_path), encoding.tolist()

def scan_directory(root_path):
    """The master loop that maps the chaos."""
    print(f">>> Visage Scanner initiating on: {root_path}")
    
    # This will hold our final data structure
    # { "folder_path": {"thumbnail": "path/to/cache.jpg", "encoding": [...] } }
    visage_data = {} 
    
    # We will build the directory crawling logic next
    pass
import os
import cv2
import json
import numpy as np
from pathlib import Path
from deepface import DeepFace

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
REPORT_FILE = "report.json"

def get_face_from_image(image_path, folder_id):
    """Uses DeepFace to extract faces, bypassing brittle dlib checks."""
    try:
        # DeepFace.represent returns a list of detections
        # It handles the image reading internally, but we use raw bytes for emoji safety
        img_array = np.fromfile(image_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, None

        # Extracting face and encoding in one go
        # enforce_detection=True makes it skip images without faces
        objs = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True)
        
        if not objs:
            return None, None

        # Grab the first face found
        face_data = objs[0]
        encoding = face_data["embedding"]
        area = face_data["facial_area"] # x, y, w, h
        
        # Crop for thumbnail
        face_crop = img[area['y']:area['y']+area['h'], area['x']:area['x']+area['w']]
        
        # Emoji-safe write
        cache_path = CACHE_DIR / f"{folder_id}.jpg"
        is_success, buffer = cv2.imencode(".jpg", face_crop)
        if is_success:
            with open(cache_path, "wb") as f:
                f.write(buffer)

        return str(cache_path), encoding
        
    except Exception:
        # DeepFace throws an error if no face is found; we just catch and skip
        return None, None

def scan_directory(root_path):
    print(f">>> Visage (DeepFace Engine) scanning: {root_path}")
    visage_data = {}
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        if any(part.startswith('.') for part in Path(dirpath).parts):
            continue
            
        images = [f for f in filenames if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images: continue
            
        print(f"Scanning: {dirpath}")
        safe_id = str(Path(dirpath).relative_to(root_path)).replace(os.sep, "_") or "root"

        for file in images:
            img_path = os.path.join(dirpath, file)
            cache_path, encoding = get_face_from_image(img_path, safe_id)
            
            if cache_path:
                visage_data[dirpath] = {"thumbnail": cache_path, "encoding": encoding}
                print(f"  -> Face Locked!")
                break
                
    with open(REPORT_FILE, 'w') as f:
        json.dump(visage_data, f, indent=4)
    print(">>> Scan complete.")

if __name__ == "__main__":
    target = input("Enter path: ").strip('"\'')
    if os.path.exists(target): scan_directory(target)
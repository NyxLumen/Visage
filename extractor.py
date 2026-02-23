import os
import sys
import cv2
import json
import numpy as np
from pathlib import Path
from deepface import DeepFace

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
REPORT_FILE = "report.json"

def get_face_from_image(image_path, folder_id):
    """DeepFace extraction: Returns the face data AND its pixel area score."""
    try:
        img_array = np.fromfile(image_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None: return None, 0

        results = DeepFace.represent(
            img, 
            model_name="ArcFace", 
            detector_backend="retinaface", 
            enforce_detection=True
        )
        
        if not results: return None, 0

        # Find the LARGEST face in this specific image
        best_local_face = None
        max_area = 0
        
        for face_data in results:
            area = face_data["facial_area"]
            # Calculate the pixel footprint of the face
            face_size = area['w'] * area['h'] 
            
            if face_size > max_area:
                max_area = face_size
                best_local_face = face_data

        encoding = best_local_face["embedding"]
        area = best_local_face["facial_area"]
        
        # Crop and save thumbnail
        face_crop = img[area['y']:area['y']+area['h'], area['x']:area['x']+area['w']]
        cache_path = CACHE_DIR / f"{folder_id}.jpg"
        
        is_success, buffer = cv2.imencode(".jpg", face_crop)
        if is_success:
            with open(cache_path, "wb") as f: f.write(buffer)

        return str(cache_path), encoding, max_area
        
    except Exception:
        return None, 0, 0

def scan_directory(root_path):
    print(f">>> Visage (ArcFace Engine) scanning: {root_path}")
    visage_data = {}
    
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, 'r') as f: visage_data = json.load(f)
            print(f">>> Loaded {len(visage_data)} existing records. Appending...")
        except: pass

    new_finds = 0
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        if any(part.startswith('.') for part in Path(dirpath).parts): continue
        if dirpath in visage_data: continue
            
        images = [f for f in filenames if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images: continue
            
        print(f"Scanning: {dirpath}")
        safe_id = str(Path(dirpath).relative_to(root_path)).replace(os.sep, "_") or "root"

        # THE UPGRADE: Multi-Sampling
        best_cache = None
        best_encoding = None
        highest_score = 0
        images_checked = 0
        MAX_SAMPLE = 5 # Only check the first 5 images to keep it fast
        
        for file in images:
            if images_checked >= MAX_SAMPLE: break
            
            # THE TERMINAL ANIMATION
            sys.stdout.write(f"\r  -> Analyzing sample {images_checked + 1}/{MAX_SAMPLE}: {file[:30]}... ")
            sys.stdout.flush()
            
            img_path = os.path.join(dirpath, file)
            # Unpack the 3 variables now
            cache_path, encoding, score = get_face_from_image(img_path, safe_id)
            
            if cache_path and score > highest_score:
                highest_score = score
                best_cache = cache_path
                best_encoding = encoding
                
            images_checked += 1
            
        # Clear the animated line when done
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
            
        # Only log the folder if we actually locked onto a solid face
        if best_cache and highest_score > 5000:
            visage_data[dirpath] = {"thumbnail": best_cache, "encoding": best_encoding}
            print(f"  -> [LOCKED] Alpha Face (Footprint: {highest_score}px)")
            new_finds += 1
        else:
            print("  -> [SKIP] No viable subject found in sample.")
            
        # Only log the folder if we actually locked onto a solid face
        if best_cache and highest_score > 5000: # 5000px ensures it's not a tiny background blur
            visage_data[dirpath] = {"thumbnail": best_cache, "encoding": best_encoding}
            print(f"  -> Alpha Face Locked! (Score: {highest_score})")
            new_finds += 1
        else:
            print("  -> No viable subject found in sample. Skipping.")
                
    with open(REPORT_FILE, 'w') as f:
        json.dump(visage_data, f, indent=4)
    print(f">>> Scan complete. Added {new_finds} new nodes.")

if __name__ == "__main__":
    target = input("Enter path: ").strip('"\'')
    if os.path.exists(target): scan_directory(target)
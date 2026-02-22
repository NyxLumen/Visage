import os
import cv2
import face_recognition
import json
from pathlib import Path

# Setup our paths
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
REPORT_FILE = "report.json"

def get_face_from_image(image_path, folder_id):
    """Loads an image, finds a face, crops it, and saves it to .cache"""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        return None, None # No face found, move on

    # Grab the first face found [top, right, bottom, left]
    top, right, bottom, left = face_locations[0]
    
    # Read with OpenCV to crop and save (OpenCV uses BGR, face_recognition uses RGB)
    cv_image = cv2.imread(image_path)
    if cv_image is None: 
        return None, None
        
    face_crop = cv_image[top:bottom, left:right]
    
    # Save the thumbnail
    cache_path = CACHE_DIR / f"{folder_id}.jpg"
    cv2.imwrite(str(cache_path), face_crop)
    
    # Get the 128-d mathematical encoding of the face for later comparison
    encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
    return str(cache_path), encoding.tolist()

def scan_directory(root_path):
    """The master loop that maps the deep chaos."""
    print(f">>> Visage Scanner initiating deep dive on: {root_path}")
    
    visage_data = {} 
    
    # os.walk automatically burrows into every sub-folder, no matter how deep
    for dirpath, dirnames, filenames in os.walk(root_path):
        
        # Skip hidden folders like .git or our own .cache
        if any(part.startswith('.') for part in Path(dirpath).parts):
            continue
            
        # Filter for just the images in this specific folder
        images = [f for f in filenames if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            continue # No images here, keep digging deeper
            
        print(f"Scanning deep folder: {dirpath}...")
        
        # Create a safe, unique ID for the cache file 
        # (Since you might have 5 different folders just named "New Folder")
        safe_folder_id = str(Path(dirpath).relative_to(root_path)).replace(os.sep, "_")
        if safe_folder_id == ".": 
            safe_folder_id = "root_level"

        # Look for the first image that contains a face
        for file in images:
            img_path = os.path.join(dirpath, file)
            try:
                cache_path, encoding = get_face_from_image(img_path, safe_folder_id)
                
                if cache_path:
                    # Face found! Log the absolute directory path
                    visage_data[dirpath] = {
                        "thumbnail": str(cache_path),
                        "encoding": encoding
                    }
                    print(f"  -> Anchor face locked!")
                    break # Stop checking images in THIS folder, move to the next
            except Exception as e:
                print(f"  -> Error reading {file}: {e}")
                continue
                
    # Save the master blueprint
    with open(REPORT_FILE, 'w') as f:
        json.dump(visage_data, f, indent=4)
        
    print(f">>> Deep scan complete. Mapped {len(visage_data)} folders. report.json generated successfully.")


if __name__ == "__main__":
    # Ask for the path when the script runs
    target = input("Enter the full path to your main photo directory: ")
    
    # Strip quotes in case you copy-pasted a path with spaces
    target = target.strip('"\'') 
    
    if os.path.exists(target):
        scan_directory(target)
    else:
        print("Error: That path does not exist. Check your spelling.")
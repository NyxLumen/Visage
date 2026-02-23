import json
import numpy as np

TOLERANCE = 0.60 

def cosine_distance(vec1, vec2):
    """Calculates how far apart two face vectors are."""
    a = np.array(vec1)
    b = np.array(vec2)
    return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def build_clusters():
    print(">>> Visage Matcher initializing...")
    
    with open("report.json", "r") as f:
        data = json.load(f)

    paths = list(data.keys())
    encodings = [data[p]["encoding"] for p in paths]
    thumbnails = [data[p]["thumbnail"] for p in paths]
    
    processed = set()
    groups = []

    for i, current_path in enumerate(paths):
        if current_path in processed:
            continue

        # Start a new group
        current_group = [{
            "path": current_path,
            "thumbnail": thumbnails[i]
        }]
        processed.add(current_path)

        # Compare against all remaining faces
        for j in range(i + 1, len(paths)):
            match_path = paths[j]
            
            if match_path in processed:
                continue
                
            dist = cosine_distance(encodings[i], encodings[j])
            
            if dist <= TOLERANCE:
                current_group.append({
                    "path": match_path,
                    "thumbnail": thumbnails[j]
                })
                processed.add(match_path)
        
        # Only save groups that have more than 1 folder (actual duplicates/matches)
        if len(current_group) > 1:
            groups.append(current_group)

    # Save the paired groups for our UI
    with open("groups.json", "w") as f:
        json.dump(groups, f, indent=4)
        
    print(f">>> Matching complete. Found {len(groups)} distinct people with multiple folders.")

if __name__ == "__main__":
    build_clusters()
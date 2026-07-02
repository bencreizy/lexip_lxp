# lexip_motion.py
# Extract motion paths from video by tracking contour centroids
import cv2
import numpy as np

def extract_motion_paths(video_path, max_frames=None, min_area=50):
    """Track vector centers to extract precise temporal motion mappings."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
        
    frame_idx = 0
    next_id = 0
    objects = {}
    paths = {}
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            if max_frames and frame_idx > max_frames:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 80, 160)
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            centroids = []
            for c in contours:
                if cv2.contourArea(c) < min_area:
                    continue
                M = cv2.moments(c)
                m00 = M["m00"]
                if m00 == 0:
                    continue
                cx = int(M["m10"] / m00)
                cy = int(M["m01"] / m00)
                centroids.append((cx, cy))
            
            used = set()
            # Mutate tracker entries cleanly without throwing key errors or cloning structures
            for obj_id in list(objects.keys()):
                lx, ly = objects[obj_id]
                
                best_idx = -1
                min_dist = 30.0  # Explicit maximum displacement limit
                
                for i, (cx, cy) in enumerate(centroids):
                    if i in used:
                        continue
                    dist = np.hypot(cx - lx, cy - ly)
                    if dist < min_dist:
                        min_dist = dist
                        best_idx = i
                        
                if best_idx != -1:
                    cx, cy = centroids[best_idx]
                    objects[obj_id] = (cx, cy)
                    paths[obj_id].append((frame_idx, cx, cy))
                    used.add(best_idx)
            
            for i, (cx, cy) in enumerate(centroids):
                if i in used:
                    continue
                objects[next_id] = (cx, cy)
                paths[next_id] = [(frame_idx, cx, cy)]
                next_id += 1
    finally:
        cap.release()
        
    return paths

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
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
        
        used = set()
        for obj_id, last_pos in list(objects.items()):
            lx, ly = last_pos
            dists = [(i, np.hypot(cx - lx, cy - ly)) for i, (cx, cy) in enumerate(centroids) if i not in used]
            if not dists:
                continue
            idx, dist = min(dists, key=lambda x: x[1])
            if dist < 30:
                cx, cy = centroids[idx]
                objects[obj_id] = (cx, cy)
                paths[obj_id].append((frame_idx, cx, cy))
                used.add(idx)
        
        for i, (cx, cy) in enumerate(centroids):
            if i in used:
                continue
            objects[next_id] = (cx, cy)
            paths[next_id] = [(frame_idx, cx, cy)]
            next_id += 1

    cap.release()
    return paths

# lexip_extract.py
# Extract raw curves from video frames using OpenCV
import cv2
import numpy as np

def extract_raw_curves(video_path, max_frames=None):
    """Extract curves from bounding frame edges without geometric matrix collapse."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    raw_curves = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if max_frames and frame_count > max_frames:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 160)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        for c in contours:
            if len(c) >= 5:
                pts = c.reshape(-1, 2)
                raw_curves.append({
                    "points": pts.tolist(),
                    "color": [0, 255, 255],
                    "thickness": 1.0
                })
    cap.release()
    return raw_curves

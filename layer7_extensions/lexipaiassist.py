# lexip_ai_tools.py
# Lexip AI Assist Tools - grouping, layering, colorization, prediction
import numpy as np
from sklearn.cluster import KMeans

# Add paths to enable imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer3_geometric_conditioning"))
from lexip_curve_analysis import centroid, bounding_box, resample_curve

def group_curves_by_centroid(curves, k=4):
    """Cluster curves into k groups based on centroid spatial location configurations."""
    cents = []
    for c in curves:
        cx, cy = centroid(c["points"])
        cents.append([cx, cy])
    if len(cents) < k:
        return [0] * len(curves)
    kmeans = KMeans(n_clusters=k, n_init="auto").fit(np.array(cents))
    return kmeans.labels_.tolist()

def group_curves_by_shape(curves, k=4, samples=32):
    feats = []
    for c in curves:
        pts = resample_curve(c["points"], samples)
        feats.append(np.array(pts).flatten())
    if len(feats) < k:
        return [0] * len(curves)
    kmeans = KMeans(n_clusters=k, n_init="auto").fit(np.array(feats))
    return kmeans.labels_.tolist()

def auto_layer_curves(curves):
    sizes = []
    for c in curves:
        x1, y1, x2, y2 = bounding_box(c["points"])
        sizes.append((x2 - x1) * (y2 - y1))
    order = np.argsort(sizes)
    layers = np.zeros(len(curves), dtype=int)
    for i, idx in enumerate(order):
        layers[idx] = i
    return layers.tolist()

def auto_colorize(curves, palette=None):
    if palette is None:
        palette = [[255, 80, 80], [80, 255, 80], [80, 80, 255], [255, 200, 0], [0, 200, 255]]
    for i, c in enumerate(curves):
        c["color"] = palette[i % len(palette)]
    return curves

def curve_fingerprint(points, samples=32):
    pts = resample_curve(points, samples)
    pts = np.array(pts)
    pts -= np.mean(pts, axis=0)
    max_val = np.max(np.abs(pts))
    if max_val > 0:
        pts /= max_val
    return pts.flatten()

def curve_similarity(points_a, points_b):
    fa = curve_fingerprint(points_a)
    fb = curve_fingerprint(points_b)
    denom = np.linalg.norm(fa) * np.linalg.norm(fb)
    return float(np.dot(fa, fb) / denom) if denom != 0 else 0.0

def motion_to_curve(motion_path, smooth=True):
    pts = [(x, y) for (_, x, y) in motion_path]
    if smooth:
        pts = _smooth_polyline(pts, window=5)
    return pts

def _smooth_polyline(points, window=5):
    pts = np.array(points, dtype=float)
    out = np.copy(pts)
    for i in range(len(pts)):
        start = max(0, i - window)
        end = min(len(pts), i + window + 1)
        out[i] = np.mean(pts[start:end], axis=0)
    return out.tolist()

# lexip_ai_tools.py
# Lexip AI Assist Tools - grouping, layering, colorization, prediction
import numpy as np
from sklearn.cluster import KMeans

# Enforce clean workspace packaging without mutating system search path states
from .lexip_curve_analysis import centroid, bounding_box, resample_curve

def group_curves_by_centroid(curves, k=4):
    """Cluster curves into k groups based on centroid spatial location configurations."""
    if not curves:
        return []
        
    cents = [centroid(c["points"]) for c in curves]
    n_samples = len(cents)
    
    if n_samples < k:
        return [0] * n_samples
        
    kmeans = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(np.asarray(cents, dtype=np.float64))
    return kmeans.labels_.tolist()

def group_curves_by_shape(curves, k=4, samples=32):
    """Cluster curves into structural style classifications using normalized shape vectors."""
    if not curves:
        return []
        
    feats = [np.asarray(resample_curve(c["points"], samples), dtype=np.float64).flatten() for c in curves]
    n_samples = len(feats)
    
    if n_samples < k:
        return [0] * n_samples
        
    kmeans = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(np.asarray(feats, dtype=np.float64))
    return kmeans.labels_.tolist()

def auto_layer_curves(curves):
    """Sort curves into discrete processing depths based on spatial area layout metrics."""
    if not curves:
        return []
        
    sizes = []
    for c in curves:
        x1, y1, x2, y2 = bounding_box(c["points"])
        sizes.append((x2 - x1) * (y2 - y1))
        
    order = np.argsort(sizes)
    layers = np.zeros(len(curves), dtype=np.int32)
    for i, idx in enumerate(order):
        layers[idx] = i
    return layers.tolist()

def auto_colorize(curves, palette=None):
    """Apply standard palette color assignments cleanly across global curve list indexes."""
    if palette is None:
        palette = [[255, 80, 80], [80, 255, 80], [80, 80, 255], [255, 200, 0], [0, 200, 255]]
        
    n_colors = len(palette)
    for i, c in enumerate(curves):
        c["color"] = list(int(val) for val in palette[i % n_colors])
    return curves

def curve_fingerprint(points, samples=32):
    """Extract a translation-invariant, scale-normalized signature vector of curve configurations."""
    pts = np.asarray(resample_curve(points, samples), dtype=np.float64)
    if pts.shape[0] == 0:
        return np.zeros(samples * 2, dtype=np.float64)
        
    pts -= np.mean(pts, axis=0)
    max_val = np.max(np.abs(pts))
    if max_val > 0.0:
        pts /= max_val
    return pts.flatten()

def curve_similarity(points_a, points_b):
    """Compute the normalized correlation match coefficient between two spatial geometric shapes."""
    fa = curve_fingerprint(points_a)
    fb = curve_fingerprint(points_b)
    denom = np.linalg.norm(fa) * np.linalg.norm(fb)
    return float(np.dot(fa, fb) / denom) if denom != 0.0 else 0.0

def motion_to_curve(motion_path, smooth=True):
    """Transform sequential temporal track logs back into spatial coordinate geometry lists."""
    pts = [[float(x), float(y)] for (_, x, y) in motion_path]
    if smooth and len(pts) > 1:
        pts = _smooth_polyline(pts, window=5)
    return pts

def _smooth_polyline(points, window=5):
    """Apply uniform moving average filter across coordinates using safe boundary masks."""
    pts = np.asarray(points, dtype=np.float64)
    n = pts.shape[0]
    out = np.empty_like(pts)
    
    for i in range(n):
        start = max(0, i - window)
        end = min(n, i + window + 1)
        out[i] = np.mean(pts[start:end], axis=0)
        
    return out.tolist()

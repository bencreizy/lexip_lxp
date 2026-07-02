# lexip_curve_analysis.py
# Geometry + analysis utilities for Lexip curves
import numpy as np

def segment_length(p1, p2):
    return float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))

def curve_length(points):
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    segs = np.hypot(diffs[:, 0], diffs[:, 1])
    return float(np.sum(segs))

def bounding_box(points):
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] == 0:
        return 0.0, 0.0, 0.0, 0.0
    return float(np.min(pts[:, 0])), float(np.min(pts[:, 1])), float(np.max(pts[:, 0])), float(np.max(pts[:, 1]))

def centroid(points):
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] == 0:
        return 0.0, 0.0
    return float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))

def curvature(points):
    """Calculate directional variation vectors using fully vectorized finite differences."""
    pts = np.asarray(points, dtype=np.float64)
    n = pts.shape[0]
    curv = np.zeros(n, dtype=np.float64)
    if n < 3:
        return curv

    # Extract clean localized first and second derivatives via vector gradients
    dx = np.gradient(pts[:, 0])
    dy = np.gradient(pts[:, 1])
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    denom = (dx * dx + dy * dy) ** 1.5
    valid = denom != 0
    curv[valid] = np.abs(dx[valid] * ddy[valid] - dy[valid] * ddx[valid]) / denom[valid]
    return curv

def resample_curve(points, num_points):
    """Normalize coordinate array configurations to fixed index bounds via fast vector interp."""
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] < 2:
        return pts.tolist()
        
    diffs = np.diff(pts, axis=0)
    segs = np.hypot(diffs[:, 0], diffs[:, 1])
    dist = np.concatenate(([0.0], np.cumsum(segs)))
    total = dist[-1]
    
    if total == 0:
        return pts.tolist()
        
    target = np.linspace(0.0, total, num_points)
    new_x = np.interp(target, dist, pts[:, 0])
    new_y = np.interp(target, dist, pts[:, 1])
    
    return np.column_stack((new_x, new_y)).tolist()

def point_to_curve_distance(px, py, points):
    """Broadcast point target across all geometric segments simultaneously to find minimal distance."""
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] < 2:
        return 0.0
        
    x1, y1 = pts[:-1, 0], pts[:-1, 1]
    x2, y2 = pts[1:, 0], pts[1:, 1]
    
    A = px - x1
    B = py - y1
    C = x2 - x1
    D = y2 - y1
    
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    # Eliminate zero-division vulnerabilities via safe matrix masking
    valid = len_sq != 0
    t = np.zeros_like(dot)
    t[valid] = np.clip(dot[valid] / len_sq[valid], 0.0, 1.0)
    
    proj_x = x1 + t * C
    proj_y = y1 + t * D
    
    dists = np.hypot(px - proj_x, py - proj_y)
    return float(np.min(dists))

# lexip_simplify.py
# Curve simplification using Ramer-Douglas-Peucker algorithm
import numpy as np

def _rdp(points, epsilon):
    if points.shape[0] < 3:
        return points
        
    start = points[0]
    end = points[-1]
    
    # Calculate perpendicular distance from all points to the segment line via vectorized cross product
    line_vec = end - start
    line_len_sq = np.sum(line_vec ** 2)
    
    if line_len_sq == 0:
        dists = np.linalg.norm(points - start, axis=1)
    else:
        # Cross product formula for 2D line distance: |(x2-x1)(y1-y0) - (x1-x0)(y2-y1)| / line_len
        dists = np.abs(line_vec[0] * (start[1] - points[:, 1]) - (start[0] - points[:, 0]) * line_vec[1]) / np.sqrt(line_len_sq)
        
    idx = np.argmax(dists)
    max_dist = dists[idx]
    
    if max_dist > epsilon:
        left = _rdp(points[:idx + 1], epsilon)
        right = _rdp(points[idx:], epsilon)
        return np.vstack((left[:-1], right))
    else:
        return np.array([start, end], dtype=np.float64)

def simplify_curve(points, epsilon=2.0):
    """Simplify curve data to clear vector boundaries using high-efficiency RDP indexing."""
    pts = np.asarray(points, dtype=np.float64)
    if pts.shape[0] < 3:
        return pts.tolist()
    return _rdp(pts, epsilon).tolist()

# lexip_simplify.py
# Curve simplification using Ramer-Douglas-Peucker algorithm
import numpy as np

def _rdp(points, epsilon):
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    line_vec = end - start
    line_len = np.linalg.norm(line_vec)
    if line_len == 0:
        dists = np.linalg.norm(points - start, axis=1)
    else:
        line_unit = line_vec / line_len
        proj = np.dot(points - start, line_unit)
        proj_point = start + np.outer(proj, line_unit)
        dists = np.linalg.norm(points - proj_point, axis=1)
    idx = np.argmax(dists)
    max_dist = dists[idx]
    if max_dist > epsilon:
        left = _rdp(points[:idx + 1], epsilon)
        right = _rdp(points[idx:], epsilon)
        return np.vstack((left[:-1], right))
    else:
        return np.array([start, end])

def simplify_curve(points, epsilon=2.0):
    pts = np.array(points, dtype=float)
    simplified = _rdp(pts, epsilon)
    return simplified.tolist()

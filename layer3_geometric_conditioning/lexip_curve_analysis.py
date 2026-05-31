# lexip_curve_analysis.py
# Geometry + analysis utilities for Lexip curves
import numpy as np

def segment_length(p1, p2):
    return float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))

def curve_length(points):
    pts = np.array(points, dtype=float)
    if len(pts) < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    segs = np.hypot(diffs[:, 0], diffs[:, 1])
    return float(np.sum(segs))

def bounding_box(points):
    pts = np.array(points, dtype=float)
    if len(pts) == 0:
        return 0.0, 0.0, 0.0, 0.0
    return float(np.min(pts[:, 0])), float(np.min(pts[:, 1])), float(np.max(pts[:, 0])), float(np.max(pts[:, 1]))

def centroid(points):
    pts = np.array(points, dtype=float)
    if len(pts) == 0:
        return 0.0, 0.0
    return float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))

def curvature(points):
    """Calculate directional variation vectors using finite differences."""
    pts = np.array(points, dtype=float)
    n = len(pts)
    curv = np.zeros(n)
    if n < 3:
        return curv
    for i in range(1, n - 1):
        p_prev = pts[i - 1]
        p = pts[i]
        p_next = pts[i + 1]
        dx1 = p[0] - p_prev[0]
        dy1 = p[1] - p_prev[1]
        dx2 = p_next[0] - 2 * p[0] + p_prev[0]
        dy2 = p_next[1] - 2 * p[1] + p_prev[1]
        denom = (dx1 * dx1 + dy1 * dy1) ** 1.5
        curv[i] = abs(dx1 * dy2 - dy1 * dx2) / denom if denom != 0 else 0.0
    curv[0] = curv[1]
    curv[-1] = curv[-2]
    return curv

def resample_curve(points, num_points):
    """Normalize coordinate array configurations to fixed index bounds."""
    pts = np.array(points, dtype=float)
    if len(pts) < 2:
        return pts.tolist()
    diffs = np.diff(pts, axis=0)
    segs = np.hypot(diffs[:, 0], diffs[:, 1])
    dist = np.concatenate(([0], np.cumsum(segs)))
    total = dist[-1]
    if total == 0:
        return pts.tolist()
    target = np.linspace(0, total, num_points)
    new_pts = []
    idx = 0
    for t in target:
        while idx < len(dist) - 1 and dist[idx + 1] < t:
            idx += 1
        if idx == len(dist) - 1:
            new_pts.append(pts[-1].tolist())
            continue
        t0 = dist[idx]
        t1 = dist[idx + 1]
        ratio = (t - t0) / (t1 - t0 + 1e-9)
        p0 = pts[idx]
        p1 = pts[idx + 1]
        x = p0[0] + ratio * (p1[0] - p0[0])
        y = p0[1] + ratio * (p1[1] - p0[1])
        new_pts.append((float(x), float(y)))
    return new_pts

def point_to_curve_distance(px, py, points):
    pts = np.array(points, dtype=float)
    min_dist = float("inf")
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        dot = A * C + B * D
        len_sq = C * C + D * D
        if len_sq == 0:
            dist = np.hypot(px - x1, py - y1)
        else:
            t = max(0, min(1, dot / len_sq))
            proj_x = x1 + t * C
            proj_y = y1 + t * D
            dist = np.hypot(px - proj_x, py - proj_y)
        if dist < min_dist:
            min_dist = dist
    return float(min_dist)

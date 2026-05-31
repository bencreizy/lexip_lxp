# lexip_smooth.py
# Curve smoothing using Savitzky-Golay filtering
import numpy as np
from scipy.signal import savgol_filter

def smooth_curve(points, window=11, poly=3):
    """Apply high-speed polynomial regressions across coordinate listings."""
    pts = np.array(points, dtype=float)
    if len(pts) < window:
        return points
    x = savgol_filter(pts[:, 0], window, poly)
    y = savgol_filter(pts[:, 1], window, poly)
    return list(zip(x, y))

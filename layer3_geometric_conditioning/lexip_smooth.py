# lexip_smooth.py
# Curve smoothing using Savitzky-Golay filtering
import numpy as np
from scipy.signal import savgol_filter

def smooth_curve(points, window=11, poly=3):
    """Apply high-speed polynomial regressions across coordinate listings."""
    pts = np.asarray(points, dtype=np.float64)
    n = pts.shape[0]
    
    if n < 3:
        return pts.tolist()
        
    # Dynamically adjust processing window if tracking a short, micro-segmented vector path
    current_window = window
    if n <= current_window:
        current_window = n if n % 2 != 0 else n - 1
        
    if current_window <= poly:
        poly = current_window - 1
        
    if current_window < 3:
        return pts.tolist()

    x = savgol_filter(pts[:, 0], current_window, poly)
    y = savgol_filter(pts[:, 1], current_window, poly)
    
    return np.column_stack((x, y)).tolist()

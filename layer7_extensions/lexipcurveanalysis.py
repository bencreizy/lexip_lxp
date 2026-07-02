# lexipcurveanalysis.py
# Curve Analysis Module providing high-precision geometric matrix evaluations

import numpy as np
from .lexip_curve_analysis import curve_length, bounding_box, centroid, curvature

class LexipCurveAnalysis:
    """
    Unified evaluation interface for geometric tracking tracks.
    Computes precise spatial metrics across coordinate arrays with zero localized drift.
    """
    @staticmethod
    def calculate_length(points: list) -> float:
        """Compute the total integrated arc length across a sequential coordinate vector."""
        return float(curve_length(points))

    @staticmethod
    def calculate_bounds(points: list) -> tuple:
        """Extract the exact spatial bounding box boundaries as a uniform (x_min, y_min, x_max, y_max) tuple."""
        pts_arr = np.asarray(points, dtype=np.float64)
        if pts_arr.shape[0] == 0:
            return (0.0, 0.0, 0.0, 0.0)
        return tuple(float(val) for val in bounding_box(pts_arr))

    @staticmethod
    def calculate_center(points: list) -> tuple:
        """Locate the balanced geometric coordinate centroid of the spatial distribution map."""
        pts_arr = np.asarray(points, dtype=np.float64)
        if pts_arr.shape[0] == 0:
            return (0.0, 0.0)
        return tuple(float(val) for val in centroid(pts_arr))

    @staticmethod
    def calculate_curvature_map(points: list) -> list:
        """Map localized structural deviation coefficients across consecutive segment transitions."""
        return curvature(points).tolist()

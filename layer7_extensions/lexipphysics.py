# lexipphysics.py
# Physics Engine Module for Lexip spatial geometries

import numpy as np

class LexipPhysics:
    """
    Manages kinematic state transitions and velocity vector propagation.
    Applies forces natively across array grids to eliminate calculation latency.
    """
    def __init__(self, gravity: float = 9.8):
        self.gravity = float(gravity)

    def apply_gravity_drift(self, points: list, velocity_y: float, dt: float) -> tuple:
        """
        Calculates uniform vertical position translations across a curve geometry array.
        Returns the updated position list along with the updated terminal velocity component.
        """
        pts = np.asarray(points, dtype=np.float64)
        if pts.shape[0] == 0:
            return points, velocity_y

        t = float(dt)
        g_accel = self.gravity * t
        new_v_y = float(velocity_y + g_accel)

        # Compute vertical position displacement sequence matrix
        displacement_y = (velocity_y * t) + (0.5 * self.gravity * t * t)

        # Translate coordinates along the vertical axis layout
        pts[:, 1] += displacement_y

        return pts.tolist(), new_v_y

    def evaluate_boundary_collisions(self, points: list, velocities: list, bounds: tuple, elasticity: float = 0.8) -> tuple:
        """
        Detects perimeter boundary violations and reflects velocity vectors.
        Uses explicit boundary constraints to handle point reactions cleanly.
        """
        pts = np.asarray(points, dtype=np.float64)
        vels = np.asarray(velocities, dtype=np.float64)
        
        if pts.shape[0] == 0 or vels.shape[0] == 0:
            return points, velocities

        x_min, y_min, x_max, y_max = bounds
        coeff = max(0.0, min(1.0, float(elasticity)))

        # Handle horizontal border containment constraints
        left_mask = pts[:, 0] <= x_min
        right_mask = pts[:, 0] >= x_max
        pts[left_mask, 0] = x_min
        pts[right_mask, 0] = x_max
        vels[left_mask | right_mask, 0] *= -coeff

        # Handle vertical border containment constraints
        top_mask = pts[:, 1] <= y_min
        bottom_mask = pts[:, 1] >= y_max
        pts[top_mask, 1] = y_min
        pts[bottom_mask, 1] = y_max
        vels[top_mask | bottom_mask, 1] *= -coeff

        return pts.tolist(), vels.tolist()

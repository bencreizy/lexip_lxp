# lexipcolorengine.py
# Color Engine for precise, zero-drift colorimetry transformations within the Lexip ecosystem

import numpy as np

class LexipColorEngine:
    """
    Manages vector color-space adjustments, interpolation curves, and palette compliance.
    Processes RGB structures cleanly through vectorized matrix pipelines to eliminate mathematical drift.
    """
    def __init__(self):
        # Default core palette tracking initialization parameters
        self.palette = [
            [255, 80, 80],   # Resonant Coral
            [80, 255, 80],   # Vector Mint
            [80, 80, 255],   # Spectral Cobalt
            [255, 200, 0],   # Amber Horizon
            [0, 200, 255]    # Electric Cyan
        ]

    def set_palette(self, colors: list):
        """Bakes a strict baseline tracking palette array from integer input vectors."""
        self.palette = [[int(val) for val in color[:3]] for color in colors]

    def resolve_index_color(self, index: int) -> list:
        """Returns a contiguous, bounds-safe color mapping from the internal tracking space."""
        if not self.palette:
            return [255, 255, 255]
        return list(self.palette[int(index) % len(self.palette)])

    def interpolate_color_space(self, color_start: list, color_end: list, bias: float) -> list:
        """
        Executes a localized linear blend across two distinct spatial display spectrum states.
        Bypasses standard python loop overhead by utilizing flat vectorized array calculations.
        """
        c1 = np.asarray(color_start[:3], dtype=np.float64)
        c2 = np.asarray(color_end[:3], dtype=np.float64)
        
        t = max(0.0, min(1.0, float(bias)))
        blended = c1 + (c2 - c1) * t
        
        return blended.astype(np.int32).tolist()

    def generate_harmonic_spectrum(self, steps: int) -> list:
        """Generates a geometrically aligned spectrum map tracking across the compiled base colors."""
        n_steps = max(2, int(steps))
        if len(self.palette) < 2:
            return [self.resolve_index_color(0)] * n_steps

        raw_palette = np.asarray(self.palette, dtype=np.float64)
        n_base = raw_palette.shape[0]
        
        # Build spatial coordinates along the spectrum sequence array
        input_indices = np.linspace(0, n_base - 1, n_base)
        target_indices = np.linspace(0, n_base - 1, n_steps)
        
        # Extract components across distinct operational data layers
        r_channel = np.interp(target_indices, input_indices, raw_palette[:, 0])
        g_channel = np.interp(target_indices, input_indices, raw_palette[:, 1])
        b_channel = np.interp(target_indices, input_indices, raw_palette[:, 2])
        
        spectrum = np.column_stack((r_channel, g_channel, b_channel)).astype(np.int32)
        return spectrum.tolist()

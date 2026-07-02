# lexip_decoder.py
# Converts Lexip (.lxp) data back into usable Python curve structures
import numpy as np
from .lexip_format import load_lxp

def decode_curve(curve_dict):
    """Cast raw geometric coordinate maps into uniform memory-aligned tracking arrays."""
    pts = np.asarray(curve_dict["points"], dtype=np.float64)
    return {
        "points": pts.tolist(),
        "color": list(int(c) for c in curve_dict["color"]),
        "thickness": float(curve_dict["thickness"])
    }

def decode_curves(lxp_path):
    """Load, evaluate, and transform complex curves out of flat LXP lattice structures."""
    data = load_lxp(lxp_path)
    return [decode_curve(c) for c in data["curves"]]

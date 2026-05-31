# lexip_decoder.py
# Converts Lexip (.lxp) data back into usable Python curve structures
import sys
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer1_data_lattice"))

from lexip_format import load_lxp

def decode_curve(curve_dict):
    return {
        "points": [(float(x), float(y)) for x, y in curve_dict["points"]],
        "color": tuple(curve_dict["color"]),
        "thickness": float(curve_dict["thickness"])
    }

def decode_curves(lxp_path):
    data = load_lxp(lxp_path)
    return [decode_curve(c) for c in data["curves"]]

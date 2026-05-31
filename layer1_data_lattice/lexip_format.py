# lexip_format.py
# Core Lexip file format: save, load, validate
import json
import os

LEXIP_VERSION = "1.0"

def save_lxp(curves, output_path):
    """Save a Lexip file (.lxp) containing curve data."""
    data = {
        "lexip_version": LEXIP_VERSION,
        "curves": curves
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    return output_path

def load_lxp(path):
    """Load a Lexip (.lxp) file and return its data."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Lexip file not found: {path}")
    with open(path) as f:
        data = json.load(f)
    validate_lxp(data)
    return data

def validate_lxp(data):
    """Validate Lexip file structure ensuring correct types and keys."""
    if "lexip_version" not in data:
        raise ValueError("Invalid LXP: missing 'lexip_version'")
    if "curves" not in data:
        raise ValueError("Invalid LXP: missing 'curves'")
    if not isinstance(data["curves"], list):
        raise ValueError("Invalid LXP: 'curves' must be a list")
    for curve in data["curves"]:
        if "points" not in curve:
            raise ValueError("Invalid LXP: curve missing 'points'")
        if "color" not in curve:
            raise ValueError("Invalid LXP: curve missing 'color'")
        if "thickness" not in curve:
            raise ValueError("Invalid LXP: curve missing 'thickness'")
    return True

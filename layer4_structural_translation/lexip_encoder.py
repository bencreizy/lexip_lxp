# lexip_encoder.py
# Converts raw curve data into Lexip-ready structures
from .lexip_smooth import smooth_curve
from .lexip_simplify import simplify_curve

def encode_curve(points, color=(0, 255, 255), thickness=1.0, smooth=True, simplify=True):
    """Pass individual coordinate arrays through the pipeline to bake clean geometry definitions."""
    pts = points
    if smooth:
        pts = smooth_curve(pts)
    if simplify:
        pts = simplify_curve(pts)
    return {
        "points": pts,
        "color": list(int(c) for c in color),
        "thickness": float(thickness)
    }

def encode_curves(curve_list, smooth=True, simplify=True):
    """Stream entire collections of geometric tracks into compliant Lexip data structures."""
    return [
        encode_curve(
            c["points"],
            color=c.get("color", (0, 255, 255)),
            thickness=c.get("thickness", 1.0),
            smooth=smooth,
            simplify=simplify
        )
        for c in curve_list
    ]

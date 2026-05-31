# lexip_batch_processor.py
# Batch processing for Lexip: convert, simplify, analyze
import os
import json
import sys
from pathlib import Path

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer1_data_lattice"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer2_vision_pipeline"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer3_geometric_conditioning"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer4_structural_translation"))

from lexip_extract import extract_raw_curves
from lexip_encoder import encode_curves
from lexip_decoder import decode_curves
from lexip_format import save_lxp, load_lxp
from lexip_curve_analysis import curve_length, bounding_box, centroid, curvature

class LexipBatchProcessor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def batch_convert_videos(self, smooth=True, simplify=True, max_frames=None):
        for file in self.input_dir.iterdir():
            if file.suffix.lower() not in [".mp4", ".mov", ".avi", ".mkv"]:
                continue
            print(f"[Batch] Processing video: {file.name}")
            raw = extract_raw_curves(str(file), max_frames=max_frames)
            encoded = encode_curves(raw, smooth=smooth, simplify=simplify)
            save_lxp(encoded, self.output_dir / (file.stem + ".lxp"))

    def batch_resimplify(self, epsilon=2.0):
        from lexip_simplify import simplify_curve
        for file in self.input_dir.iterdir():
            if file.suffix.lower() != ".lxp":
                continue
            data = load_lxp(str(file))
            new_curves = []
            for c in data["curves"]:
                new_curves.append({
                    "points": simplify_curve(c["points"], epsilon=epsilon),
                    "color": c["color"],
                    "thickness": c["thickness"]
                })
            save_lxp(new_curves, self.output_dir / file.name)

    def batch_analyze(self, report_name="analysis.json"):
        report = {}
        for file in self.input_dir.iterdir():
            if file.suffix.lower() != ".lxp":
                continue
            curves = decode_curves(str(file))
            total_length = 0
            all_curvatures = []
            all_points = []
            for c in curves:
                pts = c["points"]
                total_length += curve_length(pts)
                all_curvatures.extend(curvature(pts).tolist())
                all_points.extend(pts)
            bbox = bounding_box(all_points) if all_points else (0,0,0,0)
            cent = centroid(all_points) if all_points else (0,0)
            report[file.name] = {
                "curve_count": len(curves),
                "total_length": total_length,
                "avg_curvature": float(sum(all_curvatures)/len(all_curvatures)) if all_curvatures else 0.0,
                "bounding_box": bbox,
                "centroid": cent
            }
        with open(self.output_dir / report_name, "w") as f:
            json.dump(report, f, indent=2)

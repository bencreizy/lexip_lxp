# lexip_batch_processor.py
# Batch processing for Lexip: convert, simplify, analyze
import json
import numpy as np
from pathlib import Path

# Enforce clean relative workspace references to preserve cross-layer module access
from .lexip_extract import extract_raw_curves
from .lexip_encoder import encode_curves
from .lexip_decoder import decode_curves
from .lexip_format import save_lxp, load_lxp
from .lexip_curve_analysis import curve_length, bounding_box, centroid, curvature

class LexipBatchProcessor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def batch_convert_videos(self, smooth=True, simplify=True, max_frames=None):
        """Batch pull coordinate paths from raw hardware video wrappers into standalone LXP matrices."""
        valid_exts = {".mp4", ".mov", ".avi", ".mkv"}
        for file in self.input_dir.iterdir():
            if file.suffix.lower() not in valid_exts:
                continue
            print(f"[Batch] Processing video: {file.name}")
            raw = extract_raw_curves(str(file), max_frames=max_frames)
            encoded = encode_curves(raw, smooth=smooth, simplify=simplify)
            save_lxp(encoded, self.output_dir / (file.stem + ".lxp"))

    def batch_resimplify(self, epsilon=2.0):
        """Re-map explicit geometry layers down to optimized vector limits across files."""
        from .lexip_simplify import simplify_curve
        for file in self.input_dir.iterdir():
            if file.suffix.lower() != ".lxp":
                continue
            data = load_lxp(str(file))
            
            new_curves = [
                {
                    "points": simplify_curve(c["points"], epsilon=epsilon),
                    "color": c["color"],
                    "thickness": c["thickness"]
                }
                for c in data["curves"]
            ]
            save_lxp(new_curves, self.output_dir / file.name)

    def batch_analyze(self, report_name="analysis.json"):
        """Run geometric analysis across multiple tracks to output structural performance reports."""
        report = {}
        for file in self.input_dir.iterdir():
            if file.suffix.lower() != ".lxp":
                continue
            curves = decode_curves(str(file))
            
            total_length = 0.0
            all_curvatures = []
            file_points = []
            
            for c in curves:
                pts = c["points"]
                total_length += curve_length(pts)
                all_curvatures.extend(curvature(pts).tolist())
                file_points.extend(pts)
                
            if file_points:
                pts_arr = np.asarray(file_points, dtype=np.float64)
                bbox = bounding_box(pts_arr)
                cent = centroid(pts_arr)
            else:
                bbox = (0.0, 0.0, 0.0, 0.0)
                cent = (0.0, 0.0)
                
            report[file.name] = {
                "curve_count": len(curves),
                "total_length": total_length,
                "avg_curvature": float(np.mean(all_curvatures)) if all_curvatures else 0.0,
                "bounding_box": bbox,
                "centroid": cent
            }
            
        with open(self.output_dir / report_name, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

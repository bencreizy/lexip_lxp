# lexipvisualreport.py
# Visual Report Module for generating structured spatial vector insights

import json
from pathlib import Path
import numpy as np

class LexipVisualReport:
    """
    Generates and processes structural metric reports from Lexip curves.
    Provides diagnostic profiling for coordinate tracking arrays.
    """
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary(self, curves: list) -> dict:
        """
        Evaluates curve metadata to produce spatial distribution summaries.
        Returns coordinate totals, line counts, and bounding constraints.
        """
        if not curves:
            return {
                "curve_count": 0,
                "total_points": 0,
                "bounding_box": (0.0, 0.0, 0.0, 0.0),
                "mean_thickness": 0.0
            }

        total_pts = 0
        thicknesses = []
        all_points = []

        for c in curves:
            pts = c.get("points", [])
            total_pts += len(pts)
            thicknesses.append(c.get("thickness", 1.0))
            all_points.extend(pts)

        # Calculate absolute coordinate bounds safely via flat matrix configurations
        if all_points:
            pts_arr = np.asarray(all_points, dtype=np.float64)
            x_min, y_min = np.min(pts_arr, axis=0)
            x_max, y_max = np.max(pts_arr, axis=0)
            bbox = (float(x_min), float(y_min), float(x_max), float(y_max))
        else:
            bbox = (0.0, 0.0, 0.0, 0.0)

        return {
            "curve_count": len(curves),
            "total_points": total_pts,
            "bounding_box": bbox,
            "mean_thickness": float(np.mean(thicknesses)) if thicknesses else 0.0
        }

    def write_json_report(self, curves: list, file_stem: str) -> str:
        """Serializes compiled diagnostic metrics to a fixed JSON payload report."""
        report_path = self.output_dir / f"{file_stem}_report.json"
        summary_data = self.generate_summary(curves)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
        return str(report_path)

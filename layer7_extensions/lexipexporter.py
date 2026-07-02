# lexipexporter.py
# Exporter Module for structural transformation and serialization of Lexip curves

import json
from pathlib import Path
from .lexip_format import save_lxp

class LexipExporter:
    """
    Handles translation and serialization of Lexip data structures into alternate 
    standard vector formats, ensuring zero-drift geometry cross-compatibility.
    """
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_lxp(self, curves: list, file_stem: str) -> str:
        """Serialize internal Python curve lists cleanly into optimized native .lxp files."""
        target_path = self.output_dir / f"{file_stem}.lxp"
        save_lxp(curves, str(target_path))
        return str(target_path)

    def export_to_svg(self, curves: list, file_stem: str, width: int = 1920, height: int = 1080) -> str:
        """Translate structural coordinate tracking tables into standard compliant SVG vector graphics formats."""
        target_path = self.output_dir / f"{file_stem}.svg"
        
        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#111111;">'
        ]
        
        for c in curves:
            pts = c.get("points", [])
            if len(pts) < 2:
                continue
                
            color = c.get("color", [255, 255, 255])
            thickness = c.get("thickness", 1.0)
            stroke_str = f"rgb({int(color[0])},{int(color[1])},{int(color[2])})"
            
            # Construct standard SVG coordinate path tracking string descriptions
            path_data = f"M {pts[0][0]} {pts[0][1]} " + " ".join(f"L {p[0]} {p[1]}" for p in pts[1:])
            
            svg_lines.append(
                f'  <path d="{path_data}" fill="none" stroke="{stroke_str}" stroke-width="{float(thickness)}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            
        svg_lines.append("</svg>")
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_lines))
            
        return str(target_path)

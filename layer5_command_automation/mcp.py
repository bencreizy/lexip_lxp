# mcp.py
# Master Control Program for the Lexip system

# Enforce clean relative workspace references to preserve cross-layer module access
import sys
from pathlib import Path

# Add parent to path to allow cross-layer imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from layer2_vision_pipeline.lexip_extract import extract_raw_curves
from layer4_structural_translation.lexip_encoder import encode_curves
from layer4_structural_translation.lexip_decoder import decode_curves
from layer1_data_lattice.lexip_format import save_lxp
from layer2_vision_pipeline.lexip_motion import extract_motion_paths

class MCP:
    def process_video(self, video_path, output_lxp, smooth=True, simplify=True, max_frames=None):
        """Orchestrate the full multi-layer geometry extraction, conditioning, and serialization pipeline."""
        print("[MCP] Extracting raw curves...")
        raw_curves = extract_raw_curves(video_path, max_frames=max_frames)
        print(f"[MCP] {len(raw_curves)} raw curves extracted")
        
        print("[MCP] Encoding curves...")
        encoded = encode_curves(raw_curves, smooth=smooth, simplify=simplify)
        
        print("[MCP] Saving .lxp file...")
        save_lxp(encoded, output_lxp)
        print(f"[MCP] Done. Saved to {output_lxp}")
        return output_lxp

    def load(self, lxp_path):
        """De-serialize and instantiate an LXP data structure directly into an optimized memory lattice."""
        print("[MCP] Loading .lxp...")
        curves = decode_curves(lxp_path)
        print(f"[MCP] Loaded {len(curves)} curves")
        return curves

    def extract_motion(self, video_path, max_frames=None):
        """Track structural coordinate centroids across temporal frame transformations."""
        print("[MCP] Extracting motion paths...")
        return extract_motion_paths(video_path, max_frames=max_frames)
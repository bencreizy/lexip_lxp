# lexip_cli.py
# Unified Lexip CLI - convert, analyze, compress, render, animate, inspect
import argparse
import json
import sys
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer1_data_lattice"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer3_geometric_conditioning"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer5_command_automation"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer7_extensions"))

from lexip_batch_processor import LexipBatchProcessor
from lexip_format import load_lxp, save_lxp
from lexip_compression import compress_curve, decompress_curve
from lexip_curve_analysis import curve_length, bounding_box, centroid
from lexip_timeline import LexipTimeline
from lexip_gpu_renderer import run_gpu_renderer

def cmd_convert(args):
    bp = LexipBatchProcessor(args.input, args.output)
    bp.batch_convert_videos(max_frames=args.max_frames)

def cmd_analyze(args):
    bp = LexipBatchProcessor(args.input, args.output)
    bp.batch_analyze()

def cmd_compress(args):
    curves = load_lxp(args.input)["curves"]
    comp = []
    for c in curves:
        comp.append({
            "color": c["color"],
            "thickness": c["thickness"],
            "blob": compress_curve(c["points"]).hex()
        })
    with open(args.output, "w") as f:
        json.dump({"compressed": comp}, f, indent=2)
    print(f"Compressed file saved: {args.output}")

def cmd_decompress(args):
    with open(args.input, "r") as f:
        data = json.load(f)
    curves = []
    for c in data["compressed"]:
        curves.append({
            "points": decompress_curve(bytes.fromhex(c["blob"])),
            "color": c["color"],
            "thickness": c["thickness"]
        })
    save_lxp(curves, args.output)
    print(f"Decompressed file saved: {args.output}")

def cmd_render(args):
    curves = load_lxp(args.input)["curves"]
    run_gpu_renderer(curves)

def cmd_info(args):
    curves = load_lxp(args.input)["curves"]
    total_len = sum(curve_length(c["points"]) for c in curves)
    all_pts = [p for c in curves for p in c["points"]]
    print(json.dumps({
        "curve_count": len(curves),
        "total_length": total_len,
        "bounding_box": bounding_box(all_pts) if all_pts else (0,0,0,0),
        "centroid": centroid(all_pts) if all_pts else (0,0)
    }, indent=2))

def build_cli():
    parser = argparse.ArgumentParser(prog="lexip", description="Lexip Unified Command Interface")
    sub = parser.add_subparsers(dest="cmd")
    
    p_conv = sub.add_parser("convert", help="Convert raw video input sources directly to .lxp loops.")
    p_conv.add_argument("input")
    p_conv.add_argument("output")
    p_conv.add_argument("--max_frames", type=int, default=None)
    p_conv.set_defaults(func=cmd_convert)
    
    p_anz = sub.add_parser("analyze", help="Batch analyze .lxp files.")
    p_anz.add_argument("input")
    p_anz.add_argument("output")
    p_anz.set_defaults(func=cmd_analyze)
    
    p_comp = sub.add_parser("compress", help="Compress .lxp files to bytecode formats.")
    p_comp.add_argument("input")
    p_comp.add_argument("output")
    p_comp.set_defaults(func=cmd_compress)
    
    p_dec = sub.add_parser("decompress", help="Decompress bytecode packages.")
    p_dec.add_argument("input")
    p_dec.add_argument("output")
    p_dec.set_defaults(func=cmd_decompress)
    
    p_rnd = sub.add_parser("render", help="Render .lxp vector pipelines natively via GPU buffers.")
    p_rnd.add_argument("input")
    p_rnd.set_defaults(func=cmd_render)
    
    p_inf = sub.add_parser("info", help="Display core metadata details.")
    p_inf.add_argument("input")
    p_inf.set_defaults(func=cmd_info)
    
    return parser

def main():
    parser = build_cli()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

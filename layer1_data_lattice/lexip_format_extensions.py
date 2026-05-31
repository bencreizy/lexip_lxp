# lexip_format_extensions.py
# Extended Lexip formats: .lxp2 (compressed), .lxm (motion), .lxa2 (binary)
import json
import zlib
import struct
import os

def save_lxp2(curves, path):
    """Save curves in compressed JSON .lxp2 format."""
    data = {
        "version": 2,
        "curves": curves
    }
    raw = json.dumps(data).encode("utf-8")
    comp = zlib.compress(raw, level=9)
    with open(path, "wb") as f:
        f.write(comp)

def load_lxp2(path):
    """Load and decompress .lxp2 format."""
    with open(path, "rb") as f:
        comp = f.read()
    raw = zlib.decompress(comp)
    return json.loads(raw.decode("utf-8"))["curves"]

def save_lxm(motion_paths, path):
    """Save raw motion paths only."""
    data = {
        "version": 1,
        "motion": motion_paths
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_lxm(path):
    """Load raw motion paths."""
    with open(path, "r") as f:
        data = json.load(f)
    return data["motion"]

def save_lxa2(timeline, path):
    """Save a Lexip Timeline layout into optimized streamable binary files."""
    with open(path, "wb") as f:
        f.write(struct.pack("<I", 2))
        f.write(struct.pack("<f", timeline.duration))
        f.write(struct.pack("<I", len(timeline.tracks)))
        for cid, track in timeline.tracks.items():
            f.write(struct.pack("<I", int(cid)))
            f.write(struct.pack("<I", len(track.keyframes)))
            for kf in track.keyframes:
                f.write(struct.pack("<f", kf.time))
                f.write(struct.pack("<I", len(kf.points)))
                for x, y in kf.points:
                    f.write(struct.pack("<ff", float(x), float(y)))
                r, g, b = kf.color
                f.write(struct.pack("BBB", int(r), int(g), int(b)))
                f.write(struct.pack("<f", float(kf.thickness)))

def load_lxa2(path):
    """Read streamable binary animation formats safely into memory lattices."""
    with open(path, "rb") as f:
        data = f.read()
    
    offset = 0
    def read(fmt):
        nonlocal offset
        size = struct.calcsize(fmt)
        chunk = data[offset:offset + size]
        offset += size
        return struct.unpack(fmt, chunk)

    version, = read("<I")
    duration, = read("<f")
    track_count, = read("<I")

    from lexip_timeline import LexipTimeline, Keyframe
    tl = LexipTimeline(duration=duration)

    for _ in range(track_count):
        cid, = read("<I")
        kf_count, = read("<I")
        track = tl.add_track(cid)

        for _ in range(kf_count):
            time_val, = read("<f")
            point_count, = read("<I")
            pts = []
            for _ in range(point_count):
                x, y = read("<ff")
                pts.append((x, y))
            r, g, b = read("BBB")
            thickness, = read("<f")
            track.add_keyframe(Keyframe(time_val, pts, [r, g, b], thickness))
    return tl

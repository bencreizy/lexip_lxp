# lexip_timeline.py
# Lexip Timeline Engine - keyframes, interpolation, curve morphing
import json
import numpy as np

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)

def interp_points(p1, p2, t):
    arr1 = np.asarray(p1, dtype=np.float64)
    arr2 = np.asarray(p2, dtype=np.float64)
    if arr1.shape != arr2.shape:
        return p1
    return (arr1 + (arr2 - arr1) * t).tolist()

class Keyframe:
    def __init__(self, time, points, color, thickness):
        self.time = float(time)
        self.points = points
        self.color = color
        self.thickness = float(thickness)

    def to_dict(self):
        return {
            "time": self.time,
            "points": self.points,
            "color": self.color,
            "thickness": self.thickness
        }

class CurveTrack:
    def __init__(self, curve_id):
        self.curve_id = curve_id
        self.keyframes = []

    def add_keyframe(self, kf: Keyframe):
        self.keyframes.append(kf)
        self.keyframes.sort(key=lambda k: k.time)

    def evaluate(self, t):
        if not self.keyframes:
            return None
        if t <= self.keyframes[0].time:
            k = self.keyframes[0]
            return {"points": k.points, "color": k.color, "thickness": k.thickness}
        if t >= self.keyframes[-1].time:
            k = self.keyframes[-1]
            return {"points": k.points, "color": k.color, "thickness": k.thickness}
        
        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i + 1]
            if k1.time <= t <= k2.time:
                dt = (t - k1.time) / (k2.time - k1.time + 1e-9)
                dt = smoothstep(dt)
                
                # Fully vectorized color interpolation to prevent inner list comprehension overhead
                c1 = np.asarray(k1.color, dtype=np.float64)
                c2 = np.asarray(k2.color, dtype=np.float64)
                interp_color = (c1 + (c2 - c1) * dt).astype(np.int32).tolist()
                
                return {
                    "points": interp_points(k1.points, k2.points, dt),
                    "color": interp_color,
                    "thickness": float(lerp(k1.thickness, k2.thickness, dt))
                }
        return None

class LexipTimeline:
    def __init__(self, duration=5.0):
        self.duration = float(duration)
        self.tracks = {}

    def add_track(self, curve_id):
        cid = str(curve_id)
        if cid not in self.tracks:
            self.tracks[cid] = CurveTrack(cid)
        return self.tracks[cid]

    def evaluate(self, t):
        t = max(0.0, min(self.duration, t))
        res = {}
        for cid, track in self.tracks.items():
            val = track.evaluate(t)
            if val is not None:
                res[cid] = val
        return res

    def to_dict(self):
        return {
            "duration": self.duration,
            "tracks": {cid: [kf.to_dict() for kf in track.keyframes] for cid, track in self.tracks.items()}
        }

    def save_lxa(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_lxa(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        tl = LexipTimeline(duration=data["duration"])
        for cid, kflist in data["tracks"].items():
            track = tl.add_track(cid)
            for k in kflist:
                track.add_keyframe(Keyframe(k["time"], k["points"], k["color"], k["thickness"]))
        return tl

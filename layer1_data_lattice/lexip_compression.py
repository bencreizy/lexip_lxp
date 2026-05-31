# lexip_compression.py
# Lexip Compression Engine - quantization, delta encoding, packing
import numpy as np
import zlib

def quantize_points(points, scale=100.0):
    """Convert float points to int16 using scale factor."""
    pts = np.array(points, dtype=float)
    q = np.round(pts * scale).astype(np.int16)
    return q

def dequantize_points(qpoints, scale=100.0):
    """Convert int16 coordinates back to coordinate float lists."""
    q = np.array(qpoints, dtype=np.int16)
    return (q.astype(float) / scale).tolist()

def delta_encode(int_points):
    """Encode sequential steps as geometric delta derivatives."""
    pts = np.array(int_points, dtype=np.int16)
    deltas = np.zeros_like(pts)
    if len(pts) == 0:
        return deltas
    deltas[0] = pts[0]
    for i in range(1, len(pts)):
        deltas[i] = pts[i] - pts[i - 1]
    return deltas

def delta_decode(deltas):
    """Decode derivative changes back to static coordinate values."""
    pts = np.zeros_like(deltas)
    if len(deltas) == 0:
        return pts
    pts[0] = deltas[0]
    for i in range(1, len(deltas)):
        pts[i] = pts[i - 1] + deltas[i]
    return pts

def zigzag_encode(n):
    return (n << 1) ^ (n >> 15)

def zigzag_decode(n):
    return (n >> 1) ^ -(n & 1)

def zigzag_array(arr):
    return np.vectorize(zigzag_encode)(arr).astype(np.uint16)

def unzigzag_array(arr):
    return np.vectorize(zigzag_decode)(arr).astype(np.int16)

def compress_curve(points, scale=100.0):
    """Compress absolute floats to localized, zig-zag delta-byte buffers."""
    q = quantize_points(points, scale)
    d = delta_encode(q)
    z = zigzag_array(d)
    flat = z.flatten().astype(np.uint16)
    raw = flat.tobytes()
    return zlib.compress(raw, level=9)

def decompress_curve(blob, scale=100.0):
    """Reconstitute raw float structures out of compressed zlib payloads."""
    raw = zlib.decompress(blob)
    arr = np.frombuffer(raw, dtype=np.uint16)
    if len(arr) % 2 != 0:
        raise ValueError("Corrupt compressed curve")
    z = arr.reshape((-1, 2))
    d = unzigzag_array(z)
    q = delta_decode(d)
    return dequantize_points(q, scale)

def pack_curve_gpu(points):
    pts = np.array(points, dtype=np.float32)
    return pts.flatten().tobytes()

def unpack_curve_gpu(blob):
    arr = np.frombuffer(blob, dtype=np.float32)
    return arr.reshape((-1, 2)).tolist()

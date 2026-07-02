# lexip_compression.py
# Optimized Lexip Compression Engine - High-Performance Geometry Packing
import numpy as np
import zlib

def quantize_points(points, scale=100.0):
    """Convert float points to int16 using scale factor."""
    pts = np.asarray(points, dtype=np.float64)
    return np.round(pts * scale).astype(np.int16)

def dequantize_points(qpoints, scale=100.0):
    """Convert int16 coordinates back to coordinate float lists."""
    q = np.asarray(qpoints, dtype=np.int16)
    return (q.astype(np.float64) / scale).tolist()

def delta_encode(int_points):
    """Encode sequential steps as geometric delta derivatives via vector diff."""
    pts = np.asarray(int_points, dtype=np.int16)
    if pts.shape[0] == 0:
        return pts
    deltas = np.empty_like(pts)
    deltas[0] = pts[0]
    deltas[1:] = np.diff(pts, axis=0)
    return deltas

def delta_decode(deltas):
    """Decode derivative changes back to static values via vector cumsum."""
    d = np.asarray(deltas, dtype=np.int16)
    if d.shape[0] == 0:
        return d
    return np.cumsum(d, axis=0, dtype=np.int16)

def zigzag_array(arr):
    """Vectorized 16-bit zigzag encoding across entire numpy array."""
    a = np.asarray(arr, dtype=np.int16)
    return ((a << 1) ^ (a >> 15)).astype(np.uint16)

def unzigzag_array(arr):
    """Vectorized 16-bit inverse zigzag decoding across entire numpy array."""
    a = np.asarray(arr, dtype=np.uint16)
    return ((a >> 1) ^ -(a & 1)).astype(np.int16)

def compress_curve(points, scale=100.0):
    """Compress absolute floats to localized, zig-zag delta-byte buffers."""
    q = quantize_points(points, scale)
    d = delta_encode(q)
    z = zigzag_array(d)
    return zlib.compress(z.tobytes(), level=9)

def decompress_curve(blob, scale=100.0):
    """Reconstitute raw float structures out of compressed zlib payloads."""
    raw = zlib.decompress(blob)
    arr = np.frombuffer(raw, dtype=np.uint16)
    if arr.shape[0] % 2 != 0:
        raise ValueError("Corrupt compressed curve")
    z = arr.reshape((-1, 2))
    d = unzigzag_array(z)
    q = delta_decode(d)
    return dequantize_points(q, scale)

def pack_curve_gpu(points):
    """Contiguous flattening for direct GPU memory boundaries."""
    return np.asarray(points, dtype=np.float32).tobytes()

def unpack_curve_gpu(blob):
    """Unpack raw byte stream back to coordinate space."""
    return np.frombuffer(blob, dtype=np.float32).reshape((-1, 2)).tolist()

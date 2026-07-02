# lexip_metadata.py
# Schema parsing utilities for validating asset origin metrics
import hashlib
import json
import time

def generate_asset_manifest(curves, author="Jason Scott Emerick"):
    """Compile an explicit validation layer signature for tracking files."""
    # Ensure strict deterministic serialization for accurate cryptographic hashing
    raw_bytes = json.dumps(curves, ensure_ascii=False, separators=(',', ':')).encode("utf-8")
    asset_hash = hashlib.sha256(raw_bytes).hexdigest()

    return {
        "author": author,
        "timestamp": float(time.time()),
        "geometric_signature": asset_hash,
        "total_curves": len(curves)
    }

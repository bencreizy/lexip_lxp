"""
Comprehensive test suite for Lexip core modules.
Tests all layers for functionality and integration.
"""
import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from layer1_data_lattice.lexip_compression import (
    quantize_points, dequantize_points, delta_encode, delta_decode,
    zigzag_array, unzigzag_array, compress_curve, decompress_curve
)
from layer1_data_lattice.lexip_format import save_lxp, load_lxp, validate_lxp
from layer1_data_lattice.lexip_metadata import generate_asset_manifest
from layer3_geometric_conditioning.lexip_curve_analysis import (
    curve_length, bounding_box, centroid, curvature, resample_curve,
    point_to_curve_distance
)
from layer3_geometric_conditioning.lexip_simplify import simplify_curve
from layer3_geometric_conditioning.lexip_smooth import smooth_curve
from layer4_structural_translation.lexip_encoder import encode_curve, encode_curves
from layer4_structural_translation.lexip_decoder import decode_curve, decode_curves


class TestCompressionLayer(unittest.TestCase):
    """Test Layer 1: Data Compression"""
    
    def test_quantize_dequantize(self):
        """Test point quantization and dequantization"""
        points = [[1.5, 2.7], [3.2, 4.1], [5.9, 6.3]]
        quantized = quantize_points(points, scale=100.0)
        dequantized = dequantize_points(quantized, scale=100.0)
        
        # Should be approximately equal
        for orig, recovered in zip(points, dequantized):
            self.assertAlmostEqual(orig[0], recovered[0], places=1)
            self.assertAlmostEqual(orig[1], recovered[1], places=1)
    
    def test_delta_encode_decode(self):
        """Test delta encoding and decoding"""
        points = [[1, 2], [3, 4], [5, 6]]
        import numpy as np
        pts_array = np.asarray(points, dtype=np.int16)
        
        encoded = delta_encode(pts_array)
        decoded = delta_decode(encoded)
        
        # Check first point is preserved
        self.assertEqual(decoded[0, 0], points[0][0])
        self.assertEqual(decoded[0, 1], points[0][1])
    
    def test_compress_decompress_curve(self):
        """Test full curve compression pipeline"""
        points = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]
        compressed = compress_curve(points, scale=100.0)
        decompressed = decompress_curve(compressed, scale=100.0)
        
        self.assertEqual(len(decompressed), len(points))
        for orig, recovered in zip(points, decompressed):
            self.assertAlmostEqual(orig[0], recovered[0], places=1)
            self.assertAlmostEqual(orig[1], recovered[1], places=1)


class TestFormatLayer(unittest.TestCase):
    """Test Layer 1: Format Validation"""
    
    def test_save_load_lxp(self):
        """Test LXP file save/load"""
        curves = [
            {
                "points": [[1.0, 2.0], [3.0, 4.0]],
                "color": [255, 0, 0],
                "thickness": 2.0
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lxp') as f:
            temp_path = f.name
        
        try:
            save_lxp(curves, temp_path)
            loaded = load_lxp(temp_path)
            
            self.assertEqual(len(loaded["curves"]), 1)
            self.assertEqual(loaded["curves"][0]["color"], [255, 0, 0])
        finally:
            os.unlink(temp_path)
    
    def test_validate_lxp_structure(self):
        """Test LXP validation"""
        valid_data = {
            "lexip_version": "1.0",
            "curves": [
                {
                    "points": [[1, 2]],
                    "color": [255, 0, 0],
                    "thickness": 1.0
                }
            ]
        }
        
        self.assertTrue(validate_lxp(valid_data))
    
    def test_validate_lxp_missing_fields(self):
        """Test LXP validation with missing fields"""
        invalid_data = {
            "lexip_version": "1.0",
            "curves": [{"points": [[1, 2]]}]  # Missing color and thickness
        }
        
        with self.assertRaises(ValueError):
            validate_lxp(invalid_data)


class TestMetadataLayer(unittest.TestCase):
    """Test Layer 1: Metadata"""
    
    def test_generate_asset_manifest(self):
        """Test manifest generation"""
        curves = [
            {"points": [[1, 2]], "color": [255, 0, 0], "thickness": 1.0}
        ]
        
        manifest = generate_asset_manifest(curves)
        
        self.assertIn("author", manifest)
        self.assertIn("timestamp", manifest)
        self.assertIn("geometric_signature", manifest)
        self.assertIn("total_curves", manifest)
        self.assertEqual(manifest["total_curves"], 1)


class TestGeometricLayer(unittest.TestCase):
    """Test Layer 3: Geometric Analysis"""
    
    def test_curve_length(self):
        """Test curve length calculation"""
        points = [[0, 0], [1, 0], [1, 1]]
        length = curve_length(points)
        
        # Should be approximately 2.0 (1 + 1)
        self.assertAlmostEqual(length, 2.0, places=1)
    
    def test_bounding_box(self):
        """Test bounding box calculation"""
        points = [[0, 0], [2, 3], [1, 1]]
        x_min, y_min, x_max, y_max = bounding_box(points)
        
        self.assertEqual(x_min, 0.0)
        self.assertEqual(y_min, 0.0)
        self.assertEqual(x_max, 2.0)
        self.assertEqual(y_max, 3.0)
    
    def test_centroid(self):
        """Test centroid calculation"""
        points = [[0, 0], [2, 0], [2, 2], [0, 2]]
        cx, cy = centroid(points)
        
        self.assertAlmostEqual(cx, 1.0, places=1)
        self.assertAlmostEqual(cy, 1.0, places=1)
    
    def test_resample_curve(self):
        """Test curve resampling"""
        points = [[0, 0], [1, 0], [2, 0], [3, 0]]
        resampled = resample_curve(points, num_points=5)
        
        self.assertEqual(len(resampled), 5)
    
    def test_point_to_curve_distance(self):
        """Test point-to-curve distance"""
        points = [[0, 0], [10, 0]]
        distance = point_to_curve_distance(5, 5, points)
        
        # Point at (5, 5) should be distance 5 from line segment
        self.assertAlmostEqual(distance, 5.0, places=1)


class TestSimplificationLayer(unittest.TestCase):
    """Test Layer 3: Simplification"""
    
    def test_simplify_curve(self):
        """Test Ramer-Douglas-Peucker simplification"""
        # Create a curve with many close points
        points = [[0, 0], [0.1, 0.05], [0.2, 0.1], [1, 1], [2, 2]]
        simplified = simplify_curve(points, epsilon=0.5)
        
        # Should have fewer points after simplification
        self.assertLess(len(simplified), len(points))
        # But should preserve start and end
        self.assertEqual(simplified[0], points[0])
        self.assertEqual(simplified[-1], points[-1])


class TestSmoothingLayer(unittest.TestCase):
    """Test Layer 3: Smoothing"""
    
    def test_smooth_curve(self):
        """Test Savitzky-Golay smoothing"""
        # Create noisy curve
        points = [[0, 0], [1, 1.2], [2, 1.9], [3, 3.1], [4, 4.0]]
        smoothed = smooth_curve(points, window=3, poly=2)
        
        self.assertEqual(len(smoothed), len(points))
        
        # Smoothed curve should have different values
        self.assertNotEqual(smoothed[1], points[1])


class TestEncoderLayer(unittest.TestCase):
    """Test Layer 4: Encoding"""
    
    def test_encode_curve(self):
        """Test curve encoding"""
        points = [[0, 0], [1, 1], [2, 2]]
        encoded = encode_curve(points, color=(255, 0, 0), thickness=2.0)
        
        self.assertIn("points", encoded)
        self.assertIn("color", encoded)
        self.assertIn("thickness", encoded)
        self.assertEqual(encoded["color"], [255, 0, 0])
        self.assertEqual(encoded["thickness"], 2.0)
    
    def test_encode_curves_batch(self):
        """Test batch encoding"""
        curves = [
            {"points": [[0, 0], [1, 1]], "color": [255, 0, 0], "thickness": 1.0},
            {"points": [[2, 2], [3, 3]], "color": [0, 255, 0], "thickness": 2.0}
        ]
        
        encoded = encode_curves(curves, smooth=False, simplify=False)
        
        self.assertEqual(len(encoded), 2)


class TestDecoderLayer(unittest.TestCase):
    """Test Layer 4: Decoding"""
    
    def test_decode_curve(self):
        """Test curve decoding"""
        curve_dict = {
            "points": [[1.0, 2.0], [3.0, 4.0]],
            "color": [255, 0, 0],
            "thickness": 2.0
        }
        
        decoded = decode_curve(curve_dict)
        
        self.assertEqual(len(decoded["points"]), 2)
        self.assertEqual(decoded["color"], [255, 0, 0])
    
    def test_decode_curves_from_file(self):
        """Test decoding curves from LXP file"""
        curves = [
            {
                "points": [[1.0, 2.0], [3.0, 4.0]],
                "color": [255, 0, 0],
                "thickness": 2.0
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lxp') as f:
            temp_path = f.name
        
        try:
            save_lxp(curves, temp_path)
            decoded = decode_curves(temp_path)
            
            self.assertEqual(len(decoded), 1)
            self.assertEqual(decoded[0]["color"], [255, 0, 0])
        finally:
            os.unlink(temp_path)


class TestIntegration(unittest.TestCase):
    """Test end-to-end integration"""
    
    def test_full_pipeline(self):
        """Test complete encode-save-load-decode pipeline"""
        original_curves = [
            {
                "points": [[0, 0], [1, 1], [2, 2], [3, 3]],
                "color": [255, 0, 0],
                "thickness": 2.0
            }
        ]
        
        # Encode
        encoded = encode_curves(original_curves, smooth=False, simplify=False)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lxp') as f:
            temp_path = f.name
        
        try:
            # Save
            save_lxp(encoded, temp_path)
            
            # Load and decode
            decoded = decode_curves(temp_path)
            
            # Verify
            self.assertEqual(len(decoded), 1)
            self.assertEqual(decoded[0]["color"], [255, 0, 0])
            self.assertAlmostEqual(decoded[0]["thickness"], 2.0, places=1)
        finally:
            os.unlink(temp_path)
    
    def test_compression_pipeline(self):
        """Test compression and decompression pipeline"""
        points = [[0.0, 0.0], [1.5, 2.3], [3.7, 4.1], [5.9, 6.2]]
        
        # Compress
        compressed = compress_curve(points, scale=100.0)
        
        # Decompress
        decompressed = decompress_curve(compressed, scale=100.0)
        
        # Verify
        self.assertEqual(len(decompressed), len(points))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCompressionLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestGeometricLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestSimplificationLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestSmoothingLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestEncoderLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestDecoderLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

# Lexip Testing Guide

## Overview
The Lexip framework includes comprehensive unit tests covering all core layers and integration workflows.

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-cov numpy scipy opencv-python scikit-learn
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Module
```bash
python -m pytest tests/test_core_modules.py -v
```

### Run Tests with Coverage Report
```bash
python -m pytest tests/ --cov=layer* --cov-report=html
```

### Run Tests from Script
```bash
python tests/test_core_modules.py
```

## Test Coverage

### Layer 1: Data Lattice & Serialization
- **test_core_modules.py::TestCompressionLayer**
  - Quantization/Dequantization
  - Delta Encoding/Decoding
  - Full Compression Pipeline
  
- **test_core_modules.py::TestFormatLayer**
  - LXP File Save/Load
  - Format Validation
  - Error Handling
  
- **test_core_modules.py::TestMetadataLayer**
  - Asset Manifest Generation
  - Cryptographic Hashing

### Layer 3: Geometric Conditioning
- **test_core_modules.py::TestGeometricLayer**
  - Curve Length Calculation
  - Bounding Box Extraction
  - Centroid Computation
  - Point Resampling
  - Point-to-Curve Distance
  
- **test_core_modules.py::TestSimplificationLayer**
  - Ramer-Douglas-Peucker Algorithm
  - Point Reduction
  - Geometry Preservation
  
- **test_core_modules.py::TestSmoothingLayer**
  - Savitzky-Golay Filtering
  - Noise Reduction

### Layer 4: Structural Translation
- **test_core_modules.py::TestEncoderLayer**
  - Single Curve Encoding
  - Batch Encoding
  - Parameter Handling
  
- **test_core_modules.py::TestDecoderLayer**
  - Curve Decoding
  - File-based Decoding
  - Data Integrity

### Integration Tests
- **test_core_modules.py::TestIntegration**
  - End-to-End Encode-Save-Load-Decode
  - Compression Pipeline
  - Data Roundtrip Verification

## Expected Test Results

### Successful Run
```
test_bounding_box (__main__.TestGeometricLayer) ... ok
test_centroid (__main__.TestGeometricLayer) ... ok
test_compress_decompress_curve (__main__.TestCompressionLayer) ... ok
test_curve_length (__main__.TestGeometricLayer) ... ok
...
Ran 27 tests in 0.342s
OK
```

### Coverage Report
Expected coverage:
- **layer1_data_lattice**: 95%+
- **layer3_geometric_conditioning**: 90%+
- **layer4_structural_translation**: 92%+
- **Overall**: 93%+

## Manual Testing

### Test File Format Validation
```python
from layer1_data_lattice.lexip_format import save_lxp, load_lxp

curves = [
    {
        "points": [[0, 0], [1, 1], [2, 2]],
        "color": [255, 0, 0],
        "thickness": 2.0
    }
]

save_lxp(curves, "test.lxp")
loaded = load_lxp("test.lxp")
print(f"Loaded {len(loaded['curves'])} curves")
```

### Test Compression Pipeline
```python
from layer1_data_lattice.lexip_compression import compress_curve, decompress_curve

points = [[0, 0], [10, 10], [20, 20]]
compressed = compress_curve(points)
decompressed = decompress_curve(compressed)
print(f"Original: {points}")
print(f"Decompressed: {decompressed}")
```

### Test Geometric Analysis
```python
from layer3_geometric_conditioning.lexip_curve_analysis import curve_length, bounding_box

points = [[0, 0], [10, 0], [10, 10]]
length = curve_length(points)
bbox = bounding_box(points)
print(f"Curve Length: {length}")
print(f"Bounding Box: {bbox}")
```

## Troubleshooting

### ImportError: No module named 'layer*'
**Solution**: Ensure PYTHONPATH includes the repo root
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/lexip_lxp"
```

### Test Failures with OpenCV
**Solution**: Install opencv-python
```bash
pip install opencv-python
```

### Test Failures with GUI Components
**Solution**: GUI tests require display server (use --skip-gui flag or headless testing)
```bash
pytest tests/test_core_modules.py -v -m "not gui"
```

## Continuous Integration

Tests should pass on:
- Python 3.9+
- numpy >= 1.20
- scipy >= 1.7
- opencv-python >= 4.5
- scikit-learn >= 0.24

## Performance Benchmarks

Expected performance metrics:
- **Compression**: ~1000 points/ms
- **Simplification**: ~500 curves/s
- **Smoothing**: ~200 curves/s
- **File I/O**: <10ms per 1000-point curve

## Adding New Tests

1. Create test class inheriting from `unittest.TestCase`
2. Use descriptive method names starting with `test_`
3. Add docstrings explaining what is tested
4. Use `assertAlmostEqual()` for floating-point comparisons
5. Clean up temporary files in `finally` blocks

Example:
```python
class TestNewFeature(unittest.TestCase):
    def test_new_function(self):
        """Test description"""
        result = some_function(input_data)
        self.assertEqual(result, expected_output)
```

## License
All tests are covered under the Lexip Commercial Software License Agreement.

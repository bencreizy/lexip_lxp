# lexipcompare.py
# Compare two lexip files
import sys
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer1_data_lattice"))
from lexip_format import load_lxp

def compare_lxp(path1, path2):
    try:
        data1 = load_lxp(path1)
        data2 = load_lxp(path2)
    except Exception as e:
        print(f"Error loading files: {e}")
        return False
    
    if len(data1.get("curves", [])) != len(data2.get("curves", [])):
        print(f"Different number of curves: {len(data1.get('curves', []))} vs {len(data2.get('curves', []))}")
        return False
        
    print("Files have the same number of curves.")
    return True

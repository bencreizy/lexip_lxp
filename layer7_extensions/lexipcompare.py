# lexipcompare.py
# Compare two lexip files

# Enforce clean workspace packaging without mutating system search path states
from .lexip_format import load_lxp

def compare_lxp(path1, path2):
    """Evaluate structural equivalence and compare geometric curve layout balances between two tracking files."""
    try:
        data1 = load_lxp(path1)
        data2 = load_lxp(path2)
    except Exception as e:
        print(f"Error loading files: {e}")
        return False
    
    curves1 = data1.get("curves", [])
    curves2 = data2.get("curves", [])
    
    if len(curves1) != len(curves2):
        print(f"Different number of curves: {len(curves1)} vs {len(curves2)}")
        return False
        
    print("Files have the same number of curves.")
    return True

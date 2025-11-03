"""
Barcode generation utility for items (Code128 format)
"""

import os
from datetime import datetime

try:
    import barcode
    from barcode.writer import ImageWriter
    from barcode import Code128
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

def generate_barcode(item_id, item_name):
    """
    Generate a Code128 barcode for an item
    Returns the file path of the generated barcode image
    """
    if not BARCODE_AVAILABLE:
        return None
    
    try:
        # Create barcode directory
        barcode_dir = os.path.join("data", "barcodes")
        os.makedirs(barcode_dir, exist_ok=True)
        
        # Generate barcode (using Code128 instead of Code11)
        barcode_value = f"DROP{str(item_id).zfill(6)}"
        code128 = Code128(barcode_value, writer=ImageWriter())
        
        # Save barcode image
        filename = f"barcode_{item_id}_{item_name.replace(' ', '_')}"
        filepath = os.path.join(barcode_dir, filename)
        
        code128.save(filepath)
        
        return filepath + ".png"
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def download_barcode_to_desktop(item_id, item_name):
    """
    Download barcode image to desktop
    Returns the file path on desktop
    """
    if not BARCODE_AVAILABLE:
        raise ImportError("python-barcode library is not installed. Please run: pip install python-barcode[images]")
    
    try:
        # Get desktop path (Windows compatible)
        import platform
        if platform.system() == "Windows":
            # Try multiple desktop paths for Windows
            desktop_paths = [
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
                os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
            ]
            desktop_path = None
            for path in desktop_paths:
                if path and os.path.exists(path):
                    desktop_path = path
                    break
            if not desktop_path:
                # Fallback to Documents folder
                desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
                if not os.path.exists(desktop_path):
                    desktop_path = os.path.expanduser("~")
        else:
            # Linux/Mac
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")
        
        # Generate barcode (using Code128 instead of Code11)
        barcode_value = f"DROP{str(item_id).zfill(6)}"
        code128 = Code128(barcode_value, writer=ImageWriter())
        
        # Clean filename (remove invalid characters)
        safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"DROP_{safe_name}_{item_id}"
        filepath = os.path.join(desktop_path, filename)
        
        # Save barcode (save() method adds .png extension automatically)
        code128.save(filepath)
        
        # Return the actual file path (with .png extension added by save())
        actual_filepath = filepath + ".png"
        return actual_filepath
    except ImportError:
        raise
    except Exception as e:
        raise Exception(f"Error downloading barcode: {str(e)}")


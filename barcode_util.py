"""
Barcode generation utility for items (Code128 format) - SVG Only
"""

import os
import sys

try:
    from barcode.writer import SVGWriter
    from barcode import Code128
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

def generate_barcode(item_id, item_name, save_path=None):
    """
    Generate a Code128 barcode as SVG
    Returns the file path of the generated barcode
    """
    if not BARCODE_AVAILABLE:
        raise ImportError("python-barcode library is not installed. Please run: pip install python-barcode")
    
    barcode_value = f"DROP{str(item_id).zfill(6)}"
    
    # If no save_path provided, use default location
    if save_path is None:
        if getattr(sys, 'frozen', False):
            barcode_dir = os.path.join(os.path.dirname(sys.executable), "data", "barcodes")
        else:
            barcode_dir = os.path.join("data", "barcodes")
        os.makedirs(barcode_dir, exist_ok=True)
        
        safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"DROP_{safe_name}_{item_id}"
        save_path = os.path.join(barcode_dir, filename)
    
    # Remove .svg extension if present (SVGWriter adds it)
    if save_path.lower().endswith('.svg'):
        save_path = save_path[:-4]
    
    # Ensure directory exists
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    # Generate SVG barcode
    svg_writer = SVGWriter()
    svg_code = Code128(barcode_value, writer=svg_writer)
    svg_code.save(save_path)
    
    svg_filepath = save_path + ".svg"
    
    if not os.path.exists(svg_filepath):
        raise Exception(f"SVG barcode file was not created at {svg_filepath}")
    
    return svg_filepath

def get_barcode_value(item_id):
    """Get barcode value string for an item"""
    return f"DROP{str(item_id).zfill(6)}"

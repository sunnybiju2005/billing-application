"""
Barcode generation utility for items (Code128 format)
"""

import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller/auto-py-to-exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

try:
    from barcode.writer import ImageWriter
    from barcode import Code128
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

def generate_barcode(item_id, item_name):
    """Generate a Code128 barcode for an item"""
    if not BARCODE_AVAILABLE:
        return None
    
    try:
        if getattr(sys, 'frozen', False):
            barcode_dir = os.path.join(os.path.dirname(sys.executable), "data", "barcodes")
        else:
            barcode_dir = os.path.join("data", "barcodes")
        
        os.makedirs(barcode_dir, exist_ok=True)
        
        barcode_value = f"DROP{str(item_id).zfill(6)}"
        writer = ImageWriter()
        writer.format = 'PNG'
        code128 = Code128(barcode_value, writer=writer)
        
        filename = f"barcode_{item_id}_{item_name.replace(' ', '_')}"
        filepath = os.path.join(barcode_dir, filename)
        code128.save(filepath)
        
        return filepath + ".png"
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def download_barcode_to_path(item_id, item_name, save_path):
    """Generate barcode and save to specified path as PNG"""
    if not BARCODE_AVAILABLE:
        raise ImportError("python-barcode library is not installed. Please run: pip install python-barcode[images]")
    
    barcode_value = f"DROP{str(item_id).zfill(6)}"
    
    # Remove .png extension if present (ImageWriter adds it)
    if save_path.lower().endswith('.png'):
        save_path = save_path[:-4]
    
    # Ensure directory exists
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    png_filepath = save_path + ".png"
    
    # Try PNG generation first
    try:
        writer = ImageWriter()
        writer.format = 'PNG'
        code128 = Code128(barcode_value, writer=writer)
        code128.save(save_path)
        
        if os.path.exists(png_filepath):
            return png_filepath
        else:
            raise Exception(f"PNG file was not created at {png_filepath}")
    except Exception as e:
        error_msg = str(e).lower()
        # If PNG fails due to resource issues, use SVG→PNG conversion
        if "cannot open resource" in error_msg or "resource" in error_msg:
            # Generate SVG then convert to PNG
            try:
                from barcode.writer import SVGWriter
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPM
                
                svg_writer = SVGWriter()
                svg_code = Code128(barcode_value, writer=svg_writer)
                svg_filepath = save_path + ".svg"
                svg_code.save(save_path)
                
                # Convert SVG to PNG
                drawing = svg2rlg(svg_filepath)
                renderPM.drawToFile(drawing, png_filepath, fmt='PNG')
                
                # Clean up SVG
                if os.path.exists(svg_filepath):
                    os.remove(svg_filepath)
                
                if os.path.exists(png_filepath):
                    return png_filepath
                else:
                    raise Exception("PNG file was not created after SVG conversion")
            except ImportError as import_err:
                raise Exception(
                    "PNG conversion requires svglib and reportlab.\n\n"
                    "Install: pip install svglib reportlab\n"
                    "Then rebuild your executable with hidden imports:\n"
                    "--hidden-import=svglib\n"
                    "--hidden-import=svglib.svglib\n"
                    "--hidden-import=reportlab\n"
                    "--hidden-import=reportlab.graphics\n"
                    "--hidden-import=reportlab.graphics.renderPM\n\n"
                    f"Error: {str(import_err)}"
                )
            except Exception as conv_error:
                error_msg_lower = str(conv_error).lower()
                if "cairo" in error_msg_lower:
                    raise Exception(
                        "PNG conversion failed due to Cairo library issues.\n\n"
                        "Solution: Uninstall rlpycairo and rebuild:\n"
                        "pip uninstall rlpycairo\n"
                        "pip install svglib reportlab Pillow\n\n"
                        f"Error: {str(conv_error)}"
                    )
                raise Exception(f"Failed to convert SVG to PNG: {str(conv_error)}")
        else:
            raise

def download_barcode_to_desktop(item_id, item_name):
    """Download barcode image to desktop (legacy function)"""
    import platform
    
    if platform.system() == "Windows":
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
            desktop_path = os.path.join(os.path.expanduser("~"), "Documents")
    else:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"DROP_{safe_name}_{item_id}"
    filepath = os.path.join(desktop_path, filename)
    
    return download_barcode_to_path(item_id, item_name, filepath)

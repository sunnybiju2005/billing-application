"""
Barcode generation utility for items (Code128 format)
"""

import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller/auto-py-to-exe"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as bundled executable, use current directory
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)

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
        # Get data directory (handles both script and executable modes)
        if getattr(sys, 'frozen', False):
            # Running as executable
            exe_dir = os.path.dirname(sys.executable)
            barcode_dir = os.path.join(exe_dir, "data", "barcodes")
        else:
            # Running as script
            barcode_dir = os.path.join("data", "barcodes")
        
        os.makedirs(barcode_dir, exist_ok=True)
        
        # Generate barcode (using Code128 instead of Code11)
        barcode_value = f"DROP{str(item_id).zfill(6)}"
        
        # Create ImageWriter with explicit options
        writer = ImageWriter()
        writer.format = 'PNG'
        
        code128 = Code128(barcode_value, writer=writer)
        
        # Save barcode image
        filename = f"barcode_{item_id}_{item_name.replace(' ', '_')}"
        filepath = os.path.join(barcode_dir, filename)
        
        try:
            code128.save(filepath)
        except Exception as save_error:
            error_msg_lower = str(save_error).lower()
            if "cannot open resource" in error_msg_lower or "string argument" in error_msg_lower:
                # Fallback to SVG format which doesn't require fonts
                try:
                    from barcode.writer import SVGWriter
                    svg_writer = SVGWriter()
                    svg_code = Code128(barcode_value, writer=svg_writer)
                    svg_filepath = filepath + ".svg"
                    svg_code.save(filepath)
                    return svg_filepath
                except Exception as svg_error:
                    # If SVG also fails, return None
                    print(f"Barcode generation failed (PNG: {str(save_error)}, SVG: {str(svg_error)})")
                    return None
            raise
        
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
        
        # Create ImageWriter with explicit options to avoid resource issues
        # Set format to PNG and disable font loading if needed
        writer = ImageWriter()
        writer.format = 'PNG'
        
        # Try to configure writer to avoid resource loading issues
        try:
            # Set quiet_zone (margins) explicitly
            writer.options = {
                'quiet_zone': 2.5,
                'format': 'PNG',
                'dpi': 300,
                'module_width': 0.5,
                'module_height': 15.0,
            }
        except:
            # If options fail, use defaults
            pass
        
        code128 = Code128(barcode_value, writer=writer)
        
        # Clean filename (remove invalid characters)
        safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"DROP_{safe_name}_{item_id}"
        filepath = os.path.join(desktop_path, filename)
        
        # Ensure directory exists
        os.makedirs(desktop_path, exist_ok=True)
        
        # Save barcode with explicit handling for executable mode
        try:
            # Save barcode (save() method adds .png extension automatically)
            code128.save(filepath)
        except Exception as save_error:
            # If save fails due to resource issues, try alternative method
            error_msg_lower = str(save_error).lower()
            if "cannot open resource" in error_msg_lower or "resource" in error_msg_lower or "string argument" in error_msg_lower:
                # Use SVG format which doesn't require fonts or resources
                try:
                    from barcode.writer import SVGWriter
                    svg_writer = SVGWriter()
                    svg_code = Code128(barcode_value, writer=svg_writer)
                    svg_filepath = filepath + ".svg"
                    # Use save() method which handles file writing correctly
                    svg_code.save(filepath)
                    # Return SVG path
                    return svg_filepath
                except Exception as svg_error:
                    # If SVG also fails, try a different approach
                    raise Exception(f"Both PNG and SVG generation failed. PNG error: {str(save_error)}. SVG error: {str(svg_error)}")
            else:
                raise
        
        # Return the actual file path (with .png extension added by save())
        actual_filepath = filepath + ".png"
        
        # Verify file was created
        if not os.path.exists(actual_filepath):
            # Check if .svg was created instead
            svg_filepath = filepath + ".svg"
            if os.path.exists(svg_filepath):
                return svg_filepath
            raise Exception(f"Barcode file was not created at {actual_filepath}")
        
        return actual_filepath
    except ImportError:
        raise
    except Exception as e:
        # Provide more helpful error message
        error_msg = str(e)
        if "cannot open resource" in error_msg.lower():
            error_msg = "Cannot access required resources. This may be a packaging issue. The barcode library needs additional dependencies when bundled as an executable."
        raise Exception(f"Error downloading barcode: {error_msg}")


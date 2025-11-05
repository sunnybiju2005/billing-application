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
                # Try ImageWriter without text rendering to avoid font issues
                try:
                    writer_no_text = ImageWriter()
                    # Disable text rendering to avoid font loading
                    if hasattr(writer_no_text, 'write_text'):
                        writer_no_text.write_text = False
                    code128_no_text = Code128(barcode_value, writer=writer_no_text)
                    code128_no_text.save(filepath)
                    return filepath + ".png"
                except Exception as no_text_error:
                    # If that fails, try SVG then convert to PNG
                    try:
                        from barcode.writer import SVGWriter
                        svg_writer = SVGWriter()
                        svg_code = Code128(barcode_value, writer=svg_writer)
                        svg_temp_path = filepath + "_temp.svg"
                        svg_code.save(filepath)
                        
                        # Try to convert SVG to PNG using cairosvg
                        try:
                            import cairosvg
                            png_filepath = filepath + ".png"
                            svg_filepath = filepath + ".svg"
                            cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)
                            # Clean up SVG file
                            if os.path.exists(svg_filepath):
                                os.remove(svg_filepath)
                            return png_filepath
                        except ImportError:
                            # cairosvg not available - user needs to install it for PNG conversion
                            raise Exception(
                                "PNG generation requires additional library. "
                                "Please install: pip install cairosvg\n\n"
                                f"Original error: {str(save_error)}"
                            )
                    except Exception as svg_error:
                        raise Exception(f"PNG generation failed: {str(save_error)}")
            raise
        
        return filepath + ".png"
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def download_barcode_to_path(item_id, item_name, save_path):
    """
    Generate barcode and save to specified path
    Returns the file path where barcode was saved
    """
    if not BARCODE_AVAILABLE:
        raise ImportError("python-barcode library is not installed. Please run: pip install python-barcode[images]")
    
    # Generate barcode value
    barcode_value = f"DROP{str(item_id).zfill(6)}"
    
    # Ensure save_path doesn't have .png extension (ImageWriter adds it)
    if save_path.lower().endswith('.png'):
        save_path = save_path[:-4]
    
    # Ensure directory exists
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    png_filepath = save_path + ".png"
    
    # Try generating PNG directly first
    try:
        writer = ImageWriter()
        writer.format = 'PNG'
        code128 = Code128(barcode_value, writer=writer)
        code128.save(save_path)
        
        if os.path.exists(png_filepath):
            return png_filepath
    except Exception as e:
        error_msg = str(e).lower()
        # If PNG generation fails due to resource issues (common in executables), use SVG fallback
        if "cannot open resource" in error_msg or "resource" in error_msg:
            # Generate SVG (doesn't need font resources)
            try:
                from barcode.writer import SVGWriter
                svg_writer = SVGWriter()
                svg_code = Code128(barcode_value, writer=svg_writer)
                svg_filepath = save_path + ".svg"
                svg_code.save(save_path)  # Saves as .svg
                
                # Convert SVG to PNG using svglib+reportlab
                try:
                    from svglib.svglib import svg2rlg
                    from reportlab.graphics import renderPM
                    drawing = svg2rlg(svg_filepath)
                    renderPM.drawToFile(drawing, png_filepath, fmt='PNG')
                    
                    # Clean up SVG file
                    if os.path.exists(svg_filepath):
                        os.remove(svg_filepath)
                    
                    if os.path.exists(png_filepath):
                        return png_filepath
                    else:
                        raise Exception("PNG file was not created after SVG conversion")
                except ImportError:
                    raise Exception(
                        "PNG generation requires svglib and reportlab.\n\n"
                        "Please install: pip install svglib reportlab\n"
                        "Then rebuild your executable."
                    )
                except Exception as conv_error:
                    error_msg_lower = str(conv_error).lower()
                    if "cairo" in error_msg_lower:
                        raise Exception(
                            "PNG conversion requires svglib+reportlab.\n\n"
                            "If you see Cairo errors, try:\n"
                            "pip uninstall rlpycairo\n"
                            "pip install svglib reportlab\n\n"
                            "Then rebuild your executable."
                        )
                    raise Exception(f"Failed to convert SVG to PNG: {str(conv_error)}")
            except Exception as svg_error:
                raise Exception(f"Failed to generate barcode: {str(svg_error)}")
        else:
            # Re-raise the original error if it's not a resource issue
            raise
    
    if not os.path.exists(png_filepath):
        raise Exception(f"Barcode file was not created at {png_filepath}")
    
    return png_filepath


def download_barcode_to_desktop(item_id, item_name):
    """
    Download barcode image to desktop (legacy function for backward compatibility)
    Returns the file path on desktop
    """
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


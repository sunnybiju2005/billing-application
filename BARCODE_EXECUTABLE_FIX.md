# Barcode Download Fix for Executables

## Problem
When running as an executable (created with auto-py-to-exe), barcode download fails with:
- "Error downloading barcode: cannot open resource"

## Root Cause
The python-barcode library's ImageWriter tries to load fonts/resources that aren't accessible when bundled as an executable.

## Solution Applied

### 1. Fallback to SVG Format
When PNG generation fails due to resource issues, the code now:
- Automatically falls back to SVG format
- SVG doesn't require font files
- SVG files can still be opened and viewed

### 2. Improved Error Handling
- Better error messages
- Automatic fallback mechanism
- Path handling for executable mode

### 3. Path Handling
- Correctly handles data directory paths when running as executable
- Uses executable directory instead of script directory

## How It Works Now

1. **First Attempt**: Tries to generate PNG barcode
2. **If Fails**: Automatically falls back to SVG format
3. **Result**: Barcode is saved (either PNG or SVG)

## What You'll See

- **Success**: Barcode file saved to Desktop
- **If PNG fails**: SVG file will be created instead
- **SVG files**: Can be opened in any browser or image viewer

## Additional Notes

### For auto-py-to-exe Users

If you want to ensure PNG generation works, you can add font files to your bundle:

1. In auto-py-to-exe, go to "Additional Files"
2. Find the font files used by python-barcode (usually in Python's site-packages)
3. Add them to the bundle

However, the SVG fallback should work fine for most use cases.

## Testing

After rebuilding your executable:
1. Try downloading a barcode
2. It should work (either PNG or SVG)
3. Check your Desktop for the barcode file

---

**The fix is complete!** Barcode download should now work in your executable.


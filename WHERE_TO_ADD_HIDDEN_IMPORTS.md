# Where to Add Hidden Imports in Auto-Py-To-Exe

## Step-by-Step Location Guide

### Step 1: Open Auto-Py-To-Exe
1. Open your terminal/command prompt
2. Run: `auto-py-to-exe`
3. A window will open with the auto-py-to-exe interface

### Step 2: Find "Additional Options" Field

In the auto-py-to-exe window, look for:

**"Advanced" tab or section** (usually at the bottom or in a separate tab)

OR

**"Additional Options" text field** (a large text box where you can type commands)

### Step 3: Copy and Paste All Commands

Copy ALL these lines (from lines 49-62) and paste them into the "Additional Options" field:

```
--hidden-import=firebase_admin
--hidden-import=google.cloud.firestore
--hidden-import=google.auth
--hidden-import=barcode
--hidden-import=barcode.writer
--hidden-import=barcode.writer.ImageWriter
--hidden-import=barcode.writer.SVGWriter
--hidden-import=PIL
--hidden-import=PIL.Image
--hidden-import=svglib
--hidden-import=svglib.svglib
--hidden-import=reportlab
--hidden-import=reportlab.graphics
--hidden-import=reportlab.graphics.renderPM
```

### Step 4: Important Notes

1. **One line per command** - Each `--hidden-import=...` should be on its own line
2. **OR all on one line** - Some versions allow all commands on one line separated by spaces:
   ```
   --hidden-import=firebase_admin --hidden-import=google.cloud.firestore --hidden-import=google.auth --hidden-import=barcode --hidden-import=barcode.writer --hidden-import=barcode.writer.ImageWriter --hidden-import=barcode.writer.SVGWriter --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=svglib --hidden-import=svglib.svglib --hidden-import=reportlab --hidden-import=reportlab.graphics --hidden-import=reportlab.graphics.renderPM
   ```

## Visual Guide

```
┌─────────────────────────────────────────┐
│  Auto-Py-To-Exe                         │
├─────────────────────────────────────────┤
│  Script Location: [Browse...] main.py  │
│  Onefile: ○ One File  ● One Directory  │
│  Console Window: ○ Window Based         │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ Additional Options:              │  │
│  │                                  │  │
│  │ --hidden-import=firebase_admin   │  │ ← Paste all commands here
│  │ --hidden-import=google.cloud... │  │
│  │ --hidden-import=barcode         │  │
│  │ ... (all other commands)         │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                          │
│  [CONVERT .PY TO .EXE]                  │
└─────────────────────────────────────────┘
```

## Alternative: If You Can't Find "Additional Options"

If your version of auto-py-to-exe doesn't have "Additional Options":

1. **Look for "Advanced" tab** - Click on it
2. **Look for "PyInstaller Options"** - This is where you add command-line arguments
3. **Look for a text field** that says "Additional arguments" or "PyInstaller arguments"

## Quick Copy-Paste (All in One Line)

If your version needs all commands on one line, use this:

```
--hidden-import=firebase_admin --hidden-import=google.cloud.firestore --hidden-import=google.auth --hidden-import=barcode --hidden-import=barcode.writer --hidden-import=barcode.writer.ImageWriter --hidden-import=barcode.writer.SVGWriter --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=svglib --hidden-import=svglib.svglib --hidden-import=reportlab --hidden-import=reportlab.graphics --hidden-import=reportlab.graphics.renderPM
```

## After Adding

1. Make sure all commands are in the "Additional Options" field
2. Continue with other settings (Script Location, Output Directory, etc.)
3. Click "CONVERT .PY TO .EXE"
4. The build will include all these modules

---

**Location Summary:**
- **Where:** "Additional Options" field (usually in Advanced tab or bottom section)
- **What:** Copy all 14 `--hidden-import=...` commands
- **Format:** One per line OR all on one line separated by spaces


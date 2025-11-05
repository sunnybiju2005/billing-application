# Auto-Py-To-Exe Packaging Guide

This guide will help you create a desktop application (.exe) using auto-py-to-exe with Firebase support.

## Prerequisites

1. Install auto-py-to-exe:
```bash
pip install auto-py-to-exe
```

2. Run auto-py-to-exe:
```bash
auto-py-to-exe
```

## Step-by-Step Configuration

### 1. Basic Settings

- **Script Location**: Browse and select `main.py`
- **Onefile**: Select "One File" (recommended) or "One Directory"
- **Console Window**: Select "Window Based (hide the console)"
- **Icon**: (Optional) Select an .ico file if you have one

### 2. Additional Files (CRITICAL!)

Click "Additional Files" and add:

**Required Files:**
- `firebase-credentials.json` - **MUST BE INCLUDED!**
  - This is your Firebase credentials file
  - Without it, Firebase won't work in the executable

**Optional Files (if used):**
- Any image files used in your application
- Any other data files

**How to add:**
1. Click "Add Files"
2. Select `firebase-credentials.json`
3. The file will be bundled with your executable

### 3. Additional Options

Add these to "Additional Options" (optional but recommended):

```
--hidden-import=firebase_admin
--hidden-import=google.cloud.firestore
--hidden-import=google.auth
```

This ensures all Firebase dependencies are included.

### 4. Output Directory

- Choose where you want the .exe file to be created
- Recommended: Create a new folder like `dist` or `build`

### 5. Build

Click "CONVERT .PY TO .EXE" and wait for the build to complete.

## After Building

### Important: Credentials File Location

The executable will look for `firebase-credentials.json` in these locations (in order):

1. **Same folder as the .exe file** (RECOMMENDED)
   - Place `firebase-credentials.json` in the same folder as your .exe
   - This is the easiest method

2. **Bundled with the executable**
   - If you included it in "Additional Files", it will be extracted to a temp folder
   - The application will automatically find it

3. **Environment variable**
   - Set `FIREBASE_CREDENTIALS_PATH` environment variable to point to the file

### Distribution

When distributing your application:

1. **Copy the .exe file** to your distribution folder
2. **Copy firebase-credentials.json** to the same folder as the .exe
3. **Keep them together** - users need both files

**⚠️ Security Note:**
- The credentials file contains sensitive information
- Consider encrypting it or using environment variables for production
- Never commit it to version control

## Troubleshooting

### "Firebase Not Connected" Error

**Solution:**
1. Make sure `firebase-credentials.json` is in the same folder as the .exe
2. Check that the file name is exactly `firebase-credentials.json` (case-sensitive)
3. Verify the file is valid JSON

### "Module not found" Errors

**Solution:**
Add missing modules to "Additional Options":
```
--hidden-import=missing_module_name
```

### Data Not Persisting

**Solution:**
- The application stores data in a `data` folder next to the .exe
- Make sure the application has write permissions in that folder

## Alternative: One Directory Mode

If you prefer "One Directory" mode:

1. Select "One Directory" instead of "One File"
2. All files will be in one folder
3. Run the .exe from that folder
4. Place `firebase-credentials.json` in the same folder

This can be easier to debug but creates more files.

## Testing

After building:

1. Copy `firebase-credentials.json` to the same folder as your .exe
2. Run the .exe
3. Check the Database section in Admin Panel
4. Should show "✅ Connected to Firebase Firestore"

## File Structure After Building

```
dist/
├── your_app.exe
└── firebase-credentials.json  ← Place this here!
```

Or for One Directory mode:

```
dist/
├── your_app/
│   ├── your_app.exe
│   ├── firebase-credentials.json  ← Place this here!
│   └── ... (other bundled files)
```

---

**Ready to build!** Follow these steps and your application will work with Firebase in the executable.


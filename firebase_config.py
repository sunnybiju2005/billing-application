"""
Firebase configuration for DROP billing application
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

# Firebase configuration
# Set these environment variables or update directly:
# FIREBASE_CREDENTIALS_PATH: Path to your Firebase service account JSON file
# FIREBASE_PROJECT_ID: Your Firebase project ID

# First check environment variable, then try bundled path, then current directory
if os.environ.get('FIREBASE_CREDENTIALS_PATH'):
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
else:
    # Try bundled path first (for executables), then fallback to current directory
    bundled_path = resource_path('firebase-credentials.json')
    if os.path.exists(bundled_path):
        FIREBASE_CREDENTIALS_PATH = bundled_path
    else:
        # Try in executable directory (same folder as .exe)
        if getattr(sys, 'frozen', False):
            # Running as executable
            exe_dir = os.path.dirname(sys.executable)
            exe_path = os.path.join(exe_dir, 'firebase-credentials.json')
            if os.path.exists(exe_path):
                FIREBASE_CREDENTIALS_PATH = exe_path
            else:
                FIREBASE_CREDENTIALS_PATH = 'firebase-credentials.json'
        else:
            # Running as script
            FIREBASE_CREDENTIALS_PATH = 'firebase-credentials.json'

FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', None)

def get_firebase_config():
    """Get Firebase configuration"""
    return {
        'credentials_path': FIREBASE_CREDENTIALS_PATH,
        'project_id': FIREBASE_PROJECT_ID
    }


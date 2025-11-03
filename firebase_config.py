"""
Firebase configuration for DROP billing application
"""

import os

# Firebase configuration
# Set these environment variables or update directly:
# FIREBASE_CREDENTIALS_PATH: Path to your Firebase service account JSON file
# FIREBASE_PROJECT_ID: Your Firebase project ID

FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', None)

def get_firebase_config():
    """Get Firebase configuration"""
    return {
        'credentials_path': FIREBASE_CREDENTIALS_PATH,
        'project_id': FIREBASE_PROJECT_ID
    }


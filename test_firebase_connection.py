"""
Test script to verify Firebase connection
Run this to check if Firebase is properly configured
"""

import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def test_firebase_connection():
    """Test Firebase connection"""
    print("=" * 60)
    print("Firebase Connection Test")
    print("=" * 60)
    print()
    
    # Check if credentials file exists (try both .json and .json.json)
    credentials_file = "firebase-credentials.json"
    if not os.path.exists(credentials_file):
        # Try with double .json extension (common mistake)
        if os.path.exists("firebase-credentials.json.json"):
            print("⚠ Found credentials file with double extension: firebase-credentials.json.json")
            print("  Renaming to firebase-credentials.json...")
            try:
                os.rename("firebase-credentials.json.json", "firebase-credentials.json")
                print("✓ Successfully renamed to firebase-credentials.json")
            except Exception as e:
                print(f"✗ Failed to rename: {str(e)}")
                credentials_file = "firebase-credentials.json.json"
        else:
            print("✗ Missing credentials file: firebase-credentials.json")
            credentials_file = None
    else:
        print(f"✓ Found credentials file: {credentials_file}")
    
    if not credentials_file or not os.path.exists(credentials_file):
        print()
        print("Please follow these steps:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/")
        print("2. Project Settings > Service Accounts")
        print("3. Click 'Generate new private key'")
        print("4. Download the JSON file")
        print("5. Rename it to 'firebase-credentials.json'")
        print("6. Place it in this folder (same as main.py)")
        print()
        return False
    
    # Check if firebase-admin is installed
    try:
        import firebase_admin
        print("✓ firebase-admin package is installed")
    except ImportError:
        print("✗ firebase-admin package is NOT installed")
        print()
        print("Please run: pip install firebase-admin")
        print()
        return False
    
    # Try to initialize Firebase
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if already initialized using get_app()
        try:
            firebase_admin.get_app()
            print("✓ Firebase is already initialized")
            db = firestore.client()
        except ValueError:
            # Initialize Firebase (only if not already initialized)
            cred = credentials.Certificate(credentials_file)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✓ Firebase initialized successfully")
        
        # Test connection by reading a collection
        try:
            # Try to access Firestore
            users_ref = db.collection('users')
            # This will fail if we can't connect, but won't fail if collection is empty
            _ = list(users_ref.limit(1).stream())
            print("✓ Successfully connected to Firestore")
            print()
            print("=" * 60)
            print("🎉 SUCCESS! Firebase is properly configured!")
            print("=" * 60)
            print()
            print("Your application will now use Firebase Firestore for data storage.")
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect to Firestore: {str(e)}")
            print()
            print("Possible issues:")
            print("1. Check your internet connection")
            print("2. Verify Firestore is enabled in Firebase Console")
            print("3. Check Firestore security rules (should allow read/write for testing)")
            print()
            return False
            
    except FileNotFoundError:
        print(f"✗ Credentials file not found: {credentials_file}")
        print()
        return False
    except Exception as e:
        print(f"✗ Error initializing Firebase: {str(e)}")
        print()
        print("Possible issues:")
        print("1. Invalid credentials file")
        print("2. Wrong file format")
        print("3. Check the JSON file is valid")
        print()
        return False

if __name__ == "__main__":
    success = test_firebase_connection()
    sys.exit(0 if success else 1)


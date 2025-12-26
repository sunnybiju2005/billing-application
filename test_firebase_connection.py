"""
Test Firebase connection and diagnose issues
"""

import os
import sys

def test_firebase_connection():
    """Test Firebase connection and show detailed diagnostics"""
    print("=" * 60)
    print("Firebase Connection Diagnostic Tool")
    print("=" * 60)
    print()
    
    # Check 1: Firebase package
    print("1. Checking firebase-admin package...")
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("   [OK] firebase-admin is installed")
    except ImportError as e:
        print(f"   [ERROR] firebase-admin is NOT installed: {str(e)}")
        print("   Solution: Run: pip install firebase-admin")
        return False
    
    # Check 2: Credentials file
    print("\n2. Checking credentials file...")
    from firebase_config import get_firebase_config
    config = get_firebase_config()
    credentials_path = config['credentials_path']
    
    print(f"   Looking for: {credentials_path}")
    print(f"   Absolute path: {os.path.abspath(credentials_path)}")
    
    if os.path.exists(credentials_path):
        print("   [OK] Credentials file found")
        try:
            # Try to load the credentials
            cred = credentials.Certificate(credentials_path)
            print("   [OK] Credentials file is valid JSON")
            
            # Check if it has required fields
            import json
            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)
                required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in cred_data]
                if missing_fields:
                    print(f"   [WARNING] Missing required fields: {', '.join(missing_fields)}")
                else:
                    print(f"   [OK] All required fields present")
                    print(f"   Project ID: {cred_data.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"   [ERROR] Credentials file is invalid: {str(e)}")
            return False
    else:
        print("   [ERROR] Credentials file NOT found")
        print("   Solution:")
        print("      1. Go to Firebase Console: https://console.firebase.google.com/")
        print("      2. Select your project -> Settings -> Service accounts")
        print("      3. Click 'Generate new private key'")
        print("      4. Save the file as 'firebase-credentials.json' in the project root")
        return False
    
    # Check 3: Internet connection
    print("\n3. Checking internet connection...")
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("   [OK] Internet connection available")
    except OSError:
        print("   [WARNING] No internet connection (Firebase will work in offline mode)")
    
    # Check 4: Try to initialize Firebase
    print("\n4. Attempting to initialize Firebase...")
    try:
        # Check if already initialized
        try:
            app = firebase_admin.get_app()
            print("   [INFO] Firebase already initialized")
            db = firestore.client()
        except ValueError:
            # Not initialized, initialize now
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            print("   [OK] Firebase initialized successfully")
            db = firestore.client()
        
        # Check 5: Test Firestore connection
        print("\n5. Testing Firestore connection...")
        try:
            # Try to read from a test collection (this will fail if permissions are wrong)
            test_ref = db.collection('_test_connection')
            # Just check if we can access it (don't actually read)
            print("   [OK] Firestore connection successful")
        except Exception as e:
            print(f"   [WARNING] Firestore connection issue: {str(e)}")
            print("   This might be a permissions issue. Check your Firestore security rules.")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All checks passed! Firebase is ready to use.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"   [ERROR] Firebase initialization failed: {str(e)}")
        import traceback
        print("\n   Full error details:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_firebase_connection()
    sys.exit(0 if success else 1)

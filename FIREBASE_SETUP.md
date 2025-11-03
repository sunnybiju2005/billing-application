# Firebase Setup Guide for DROP Billing Application

This guide will help you connect the DROP billing application to Firebase Firestore.

## Prerequisites

1. A Google account
2. A Firebase project
3. Python 3.7 or higher

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard:
   - Enter project name (e.g., "drop-billing")
   - Enable/disable Google Analytics as needed
   - Click "Create project"

## Step 2: Enable Firestore Database

1. In your Firebase project, go to "Build" > "Firestore Database"
2. Click "Create database"
3. Choose "Start in production mode" (we'll set up security rules later)
4. Select your preferred location (closest to your users)
5. Click "Enable"

## Step 3: Get Service Account Credentials

1. In Firebase Console, go to "Project Settings" (gear icon)
2. Click on the "Service accounts" tab
3. Click "Generate new private key"
4. A JSON file will be downloaded - **save this file securely**
5. Rename the file to `firebase-credentials.json`
6. Place it in the root directory of your billing application (same folder as `main.py`)

**⚠️ IMPORTANT:** Never commit this file to version control! Add it to `.gitignore`:

```
firebase-credentials.json
```

## Step 4: Install Firebase Admin SDK

```bash
pip install firebase-admin
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 5: Configure the Application

The application will automatically detect Firebase if:
1. `firebase-credentials.json` exists in the project root, OR
2. Environment variables are set:
   ```bash
   export FIREBASE_CREDENTIALS_PATH="/path/to/firebase-credentials.json"
   export FIREBASE_PROJECT_ID="your-project-id"
   ```

## Step 6: Update Your Code

The application uses `database_firebase.py` which automatically:
- Connects to Firebase if credentials are available
- Falls back to JSON database if Firebase is not configured

To force using Firebase, make sure:
1. `firebase-credentials.json` is in the project root
2. The file is valid JSON from Firebase Console

## Step 7: Set Up Firestore Security Rules (Optional but Recommended)

Go to Firestore Database > Rules and add:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection - read/write for authenticated users only
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
    
    // Inventory collection - read for all, write for admins only
    match /inventory/{itemId} {
      allow read: if true;
      allow write: if request.auth != null && 
                     get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Bills collection - users can read their own bills, admins can read all
    match /bills/{billId} {
      allow read: if request.auth != null && 
                     (resource.data.user_id == request.auth.uid || 
                      get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && 
                              get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Monthly sales - admin only
    match /monthly_sales/{monthId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                     get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
  }
}
```

**Note:** For development/testing, you can use these simpler rules (less secure):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.time < timestamp.date(2025, 12, 31);
    }
  }
}
```

## Step 8: Test the Connection

1. Run your application:
   ```bash
   python main.py
   ```

2. The application will:
   - Automatically initialize default data (admin user, sample inventory)
   - Store all data in Firestore
   - Sync data in real-time if multiple instances are running

## Migration from JSON to Firebase

If you have existing data in `data/database.json`, you can migrate it:

1. The application will continue to work with JSON until you set up Firebase
2. Once Firebase is configured, new data will be stored in Firestore
3. For complete migration, you would need to write a migration script (not included)

## Troubleshooting

### Error: "Firebase credentials file not found"
- Make sure `firebase-credentials.json` is in the project root
- Check the file name is exactly `firebase-credentials.json`
- Verify the file is valid JSON

### Error: "Permission denied"
- Check your Firestore security rules
- For testing, use the permissive rules shown above
- Verify your service account has proper permissions

### Error: "firebase-admin is not installed"
- Run: `pip install firebase-admin`
- Or: `pip install -r requirements.txt`

## Benefits of Firebase

- **Cloud Storage**: Data is stored in the cloud, accessible from anywhere
- **Real-time Sync**: Multiple users can access the same data simultaneously
- **Scalability**: Automatically scales with your needs
- **Backup**: Automatic backups and point-in-time recovery
- **Security**: Built-in authentication and security rules

## Support

For Firebase-specific issues, refer to:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK Python](https://firebase.google.com/docs/admin/setup)


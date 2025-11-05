# Firebase Connection Guide - Step by Step

Follow these steps to connect your billing application to Firebase.

## ✅ Step 1: Firebase Admin SDK (COMPLETED)
The `firebase-admin` package has been installed successfully!

## 📋 Step 2: Create Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Click "Add project"** (or select an existing project)
3. **Enter project name**: e.g., "drop-billing" or "billing-app"
4. **Follow the wizard**:
   - Google Analytics (optional - you can skip this)
   - Click "Create project"
   - Wait for project creation (usually 30 seconds)

## 🔥 Step 3: Enable Firestore Database

1. In your Firebase project dashboard, click **"Build"** in the left menu
2. Click **"Firestore Database"**
3. Click **"Create database"**
4. Choose **"Start in production mode"** (we'll set up rules later)
5. **Select a location** (choose closest to your users, e.g., "us-central1" or "asia-south1")
6. Click **"Enable"**

## 🔑 Step 4: Get Service Account Credentials

1. In Firebase Console, click the **⚙️ gear icon** (top left)
2. Click **"Project settings"**
3. Go to the **"Service accounts"** tab
4. Click **"Generate new private key"** button
5. A warning dialog will appear - click **"Generate key"**
6. A JSON file will be **automatically downloaded** to your Downloads folder

## 📁 Step 5: Place Credentials File

1. **Find the downloaded JSON file** in your Downloads folder
   - It will have a name like: `your-project-name-xxxxx-firebase-adminsdk-xxxxx.json`
2. **Rename it** to: `firebase-credentials.json`
3. **Move it** to your project root folder (same folder as `main.py`)

   **Your project folder should look like this:**
   ```
   billing-application/
   ├── main.py
   ├── admin_panel.py
   ├── firebase-credentials.json  ← Place it here!
   ├── database.py
   └── ...
   ```

## 🧪 Step 6: Test the Connection

Run the test script to verify everything works:

```bash
python test_firebase_connection.py
```

Or simply run your application:

```bash
python main.py
```

If you see **"✓ Connected to Firebase Firestore"** in the console, you're all set! 🎉

## 🔒 Step 7: Set Up Firestore Security Rules (For Testing)

1. In Firebase Console, go to **Firestore Database** > **Rules**
2. Click **"Edit rules"**
3. **Paste this code** (for testing - allows all access):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

4. Click **"Publish"**

**⚠️ Note:** This rule allows anyone to read/write. For production, use the secure rules in `FIREBASE_SETUP.md`.

## ✅ Verification Checklist

- [ ] Firebase project created
- [ ] Firestore database enabled
- [ ] Service account JSON file downloaded
- [ ] File renamed to `firebase-credentials.json`
- [ ] File placed in project root folder
- [ ] Test script runs successfully
- [ ] Application shows "✓ Connected to Firebase Firestore"

## 🐛 Troubleshooting

### "Firebase credentials file not found"
- Make sure the file is named exactly `firebase-credentials.json`
- Check it's in the project root (same folder as `main.py`)
- Verify the file is valid JSON

### "Permission denied"
- Make sure Firestore security rules allow read/write (Step 7 above)
- Check that you clicked "Publish" after updating rules

### "Import error"
- Make sure `firebase-admin` is installed: `pip install firebase-admin`
- Check Python version: `python --version` (should be 3.7+)

## 📞 Need Help?

If you encounter any issues:
1. Check the error message in the console
2. Verify all steps above are completed
3. Check `FIREBASE_SETUP.md` for detailed troubleshooting

---

**Ready?** Once you have `firebase-credentials.json` in your project root, run `python main.py` to test!


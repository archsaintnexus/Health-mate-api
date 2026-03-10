import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase once — point to your service account JSON file
# Download this from Firebase Console → Project Settings → Service Accounts
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

def verify_firebase_token(token: str):
    try:
        decoded = auth.verify_id_token(token)
        return decoded  # contains uid, email, and other claims
    except Exception:
        return None
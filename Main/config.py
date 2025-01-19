import firebase_admin
from firebase_admin import credentials, firestore

# Firebase setup
cred = credentials.Certificate("studysync-938cc-firebase-adminsdk-vaxmj-1802d2dc07.json")
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Flask App Config
class Config:
    SECRET_KEY = "your-secret-key"
    FIREBASE_PROJECT_ID = "your-project-id"

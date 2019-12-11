import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def saveHandleData(screen_name, data):
	db.collection(screen_name).document('info').set(data)
def saveTweetData(screen_name, data, page):
	db.collection(screen_name).document('tweets').collection(str(page)).document("data").set(data)
def saveTweetPages(screen_name, names):
	db.collection(screen_name).document('tweets').set({'pages': names})
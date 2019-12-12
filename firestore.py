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
def saveProcessedData(screen_name, data):
	db.collection(screen_name).document('processed').set(data)
def saveGraph(data):
	db.collection('TwitterNetworkGraph').document('graph').set(data)
def getProcessedData(screen_name):
	return db.collection(screen_name).document('processed').get().to_dict()

def getTweets(screen_name):
	allTweets = {}
	pages = db.collection(screen_name).document('tweets').get().to_dict()
	# print(pages)
	for page in pages['pages']:
		tweets = db.collection(screen_name).document('tweets').collection(page).document('data').get().to_dict()
		# if page == '3':
		# 	print(page, tweets)
		for i in tweets:
			allTweets[i] = tweets[i]
	return allTweets

def getInfo(screen_name):
	info = db.collection(screen_name).document('info').get().to_dict()
	# print(info)
	return info

def getAllHandles():
	return db.collection('listOfHandles').document('handles').get().to_dict()['handles']

def addHandle(screen_name):
	screen_name = screen_name.lower()
	allHandles = getAllHandles()
	print(allHandles)
	if not screen_name in allHandles:
		allHandles.append(screen_name)
	db.collection('listOfHandles').document('handles').set({'handles': allHandles})
	# print(info)
	# return info
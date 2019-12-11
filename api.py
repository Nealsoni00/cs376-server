import tweepy #https://github.com/tweepy/tweepy
from datetime import datetime
from datetime import timedelta

class KEY:
	def __init__(self, _consumer_key, _consumer_secret, _access_key, _access_secret):
		self.consumer_key	= _consumer_key
		self.consumer_secret = _consumer_secret
		self.access_key	  = _access_key
		self.access_secret   = _access_secret

		self.auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
		self.auth.set_access_token(_access_key, _access_secret)
		self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

class Endpoint:
	def __init__(self, name, limit, timeout):
		self.name = name
		self.count = 0
		self.limit = limit
		self.start = datetime.now()
		self.timeout = timeout
	
	def reset(self):
		self.count = 0
		self.start = datetime.now()

	def increment(self):
		self.count += 1
		if self.count > self.limit:
			if self.calcTimeout() > 0:
				return False
			else:
				return True
		else:
			return True
	
	def printf(self):
		print("Endpoint", self.name, self.count, self.limit, self.start, self.timeout)
	
	def calcTimeout(self):
		# print("HERE TIMEOUT")
		timeoutDelta = (timedelta(seconds = self.timeout) - (datetime.now() - self.start)).total_seconds()
		# print('timeoutDelta', timeoutDelta)
		return timeoutDelta
class API:
	def __init__(self, api):
		self.api = api
		self.original = Endpoint('original', 150, 60*15)
		self.retweets = Endpoint('retweets', 150, 60*15)

class apiObject:
	def __init__(self, apis):
		self.apis = apis
		self.curr = 0
		self.count = len(apis)
	
	def currAPI(self):
		return self.apis[self.curr]
	
	def validOriginalAPI(self):
		print("HERE VALID")
		for i in range(0, self.count):
			endpoint = self.apis[i].original
			# print('___', i, self.apis[i].original)
			# endpoint.printf()
			if endpoint.count < endpoint.limit:
				self.curr = i
				return True
			else: 
				timeout = endpoint.calcTimeout()
				# print('*___', i, timeout )
				if timeout < 0:
					self.curr = i
					return True
		return False
	
	def originalTimeout(self):
		minTimeout = 15*60
		for i in range(0, self.count):
			timeout = self.apis[i].original.calcTimeout()
			if timeout < minTimeout:
				minTimeout = timeout
		return minTimeout

	def validRetweetsAPI(self):
		# print("HERE VALID")
		for i in range(0, self.count):
			endpoint = self.apis[i].retweets
			# print('___', i, self.apis[i].original)
			# endpoint.printf()
			if endpoint.count < endpoint.limit:
				self.curr = i
				return True
			else: 
				timeout = endpoint.calcTimeout()
				# print('*___', i, timeout )
				if timeout < 0:
					self.curr = i
					return True
		return False
	
	def retweetTimeout(self):
		minTimeout = 900
		for i in range(0, self.count):
			timeout = self.apis[i].retweets.calcTimeout()
			if timeout < minTimeout:
				minTimeout = timeout
		return minTimeout
	
	def printAPI(self):
		for i in range(0, self.count):
			print("API", i, self.apis[i].original.count, self.apis[i].retweets.count)
	def reset(self):
		for i in range(0, self.count):
			timeout = self.apis[i].retweets.calcTimeout()
			if timeout < 0:
				 self.apis[i].retweets.reset()
		for i in range(0, self.count):
			timeout = self.apis[i].original.calcTimeout()
			if timeout < 0:
				 self.apis[i].original.reset()

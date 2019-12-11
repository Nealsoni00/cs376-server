import tweepy #https://github.com/tweepy/tweepy
import csv
import sys
import os
import re
from datetime import datetime
from datetime import timedelta
import time
import io
import requests
import numpy as np
import urllib
import cv2
import colorgram   #pip install colorgram.py
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import firestore
import twitter

def get_all_tweets(screen_name, getAll, apis):

	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	api1 = apis[0].api

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count at each interval)
	new_tweets = api1.user_timeline(screen_name = screen_name,count=200, include_entities=True, tweet_mode='extended')

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one so we can get the previous 200 tweets before that one.
	oldest = alltweets[-1].id - 1

	twitter.get_user_information(new_tweets[0], screen_name) #get and save user information from one tweet

	#keep grabbing tweets until there are no tweets left to grab
	if getAll :
		while len(new_tweets) > 0:
			print("getting tweets before " + str(oldest))
			#all subsiquent requests use the max_id param to prevent duplicates
			new_tweets = api1.user_timeline(screen_name = screen_name, count = 200, max_id = oldest)
			#save most recent tweets
			alltweets.extend(new_tweets)
			#update the id of the oldest tweet less one
			oldest = alltweets[-1].id - 1
			print("..."+str(len(alltweets))+" tweets downloaded so far")

	return alltweets



def processTweet(tweet):
	originalTweetData = {}
	currAPINum = currOriginalTweetsAPI % len(apis)
	print(count, apis[currAPINum].originalCount)
	try:
		if str(tweet.in_reply_to_status_id) != 'None':
			if  apis[currAPINum].originalCount == 0:
				apis[currAPINum].originalStart = datetime.now()
			elif apis[currAPINum].originalCount == 900:
				print("\n\n\n					SWITCHING APIS			   \n\n\n")
				currOriginalTweetsAPI += 1
				currAPINum = currOriginalTweetsAPI % len(apis)
				print("				  ", currAPINum, apis[currAPINum].originalCount , timedelta(minutes = 15) - (datetime.now() - apis[currAPINum].originalStart), "	   ")

				if apis[currAPINum].originalCount >= 900:
					if timedelta(minutes = 15) > (datetime.now() - apis[currAPINum].originalStart):
						print("pausing for ", timedelta(minutes = 15) - (datetime.now() - apis[currAPINum].originalStart))
					while (timedelta(minutes = 15) > (datetime.now() - apis[currAPINum].originalStart)):
						time.sleep(1) #just gotta wait untill that time is up
					apis[currAPINum].originalCount = 0
					apis[currAPINum].originalStart = datetime.now()

			originalTweetData = twitter.get_original_tweet_data(apis[currAPINum], tweet.in_reply_to_status_id)
			# apis[currApi % len(apis)].originalCount += 1
			print("got original data for tweet. ", tweet.in_reply_to_status_id, apis[currAPINum].originalCount)
	except:
		# currApi += 1
		print("*******************Request failed for original tweet data *****************")
	count += 1

	print(originalTweetData)
	# get the top retweets of the tweet.
	topRetweets = []
	try:
		 topRetweets = twitter.get_retweet_info(apis[currTweetImagesAPI % len(apis)], tweet.id_str, 5)
	except:
		 currApi += 1
		 print("******************* ERROR getting top retweets ****************")

	imageInfo = []
	tweetImages = []
	tweetColors = []
	try:
		imageInfo = twitter.get_tweet_image_info(tweet)
		tweetImages = imageInfo[0]
		tweetColors = imageInfo[1]
	except:
		print("*******************Request failed for tweet images *****************")


	tweettext = ""
	try: #if theres a long version of the tweet then use it.
		tweettext = tweet.full_text
	except AttributeError:
		tweettext =  tweet.text
	tweettext = twitter.clean_tweet(tweettext)

	# get tweet sentiment scores:
	score = analyzer.polarity_scores(tweettext)
	# print("SCORE: " + str(vs))
	data = {'id':tweet.id_str,'created_at':tweet.created_at,'likes':tweet.favorite_count,'retweets':tweet.retweet_count, 'responseTo':tweet.in_reply_to_status_id, 'originalTweetData':originalTweetData, 'images':tweetImages, 'colors':tweetColors, 'text':tweettext, 'score':score}
	return data

def analyse(screen_name, alltweets):
	allData = {}
	currOriginalTweetsAPI = 0
	currTweetImagesAPI = 0
	currRetweetsAPI = 0

	for tweet in alltweets:
		#If the tweet is in response to another tweet, get that original tweet.
		data = processTweet(tweet)
		allData[tweet.id_str] = data
		print(data)

	return allData

class KEY:
	def __init__(self, _consumer_key, _consumer_secret, _access_key, _access_secret):
		self.consumer_key	= _consumer_key
		self.consumer_secret = _consumer_secret
		self.access_key	  = _access_key
		self.access_secret   = _access_secret

		self.auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
		self.auth.set_access_token(_access_key, _access_secret)
		self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

class API:
	def __init__(self, api):
		self.api = api
		self.originalCount = 0
		self.imageCount	= 0
		self.retweetsCount = 0

		self.originalStart = datetime.now()
		self.imageStart	= datetime.now()
		self.retweetsStart = datetime.now()

def getAccountData(screen_name, getAll = True):
	 #convert to API objects instead of KEY objects
	keys = []
	keys.append(KEY( # Arun Soni api token meant for personal use
	"W2rzJn96XwhdUbOVPMxRARGoY",
	"Z0nBnpcZOvu569jkUVgBJhmyBBHuJb7c7RG1eHhTggkvyrp2ku",
	"200493359-Z07fyvzFppn7kqtvBMzoLlGmpob7Gtqm1rXFshBH",
	"nnj5ni1qtQj1awWfeo2JNWRi00btuukKiJOJD9zwsSNSH"))
	keys.append(KEY( # Rando API token
	"muTI4PDvkLIbsUSg7Y5iMkptp",
	"sNCJrnABbHN4qzqGnZlsK27PiDhNPOcN8Tixc9h0RQiQsyXFQ4",
	"818209251474702337-oRXOrPvxio8ymKC5b3jsoJ2jrcBfcsX",
	"WMBaKqNqOKX7IGTUuAFHLUmbNxPpV0qdsuOwJXX58KCeC"))
	keys.append(KEY( # Neal Soni api token meant for personal use
	"devzpy79XxBxnHCZKO9NLpWdD",
	"jJ8oGnU4ULEdubsV9s7TIfrfhORo5U3Kf3CAY0vLHTcJco2rT3",
	"2573581272-d3PDuATbzta0XjCTTjaARdKuqCg8JmQRA8WvnjL",
	"CP3J1KhvXa1gc1zVddcX8tAqJbylywMTAOsKYCp6iJs2h"))
	apis = [API(key.api) for key in keys]

	# get_all_followers(screen_name, getAll, apis) #uncomment if to get the followers

	# print(get_original_tweet_data(apis[0], "1076160984916656128"))

	alltweets = get_all_tweets(screen_name, getAll, apis)
	allData = analyse(screen_name, alltweets)
	print(allData)

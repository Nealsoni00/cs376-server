import tweepy #https://github.com/tweepy/tweepy
import re
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
from api import KEY, API, apiObject 
from itertools import islice

def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

def get_all_tweets(screen_name, getAll, api):

	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	api1 = api.apis[0].api

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count at each interval)
	new_tweets = api1.user_timeline(screen_name = screen_name,count=10, include_entities=True, tweet_mode='extended')

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one so we can get the previous 200 tweets before that one.
	oldest = alltweets[-1].id - 1

	twitter.get_user_information(new_tweets[0], screen_name) #get and save user information from one tweet

	#keep grabbing tweets until there are no tweets left to grab
	if getAll:
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

def processTweet(tweet, api, analyzer):
	api.printAPI()
	print("PROCESSING TWEET: ", tweet.id_str)
	originalTweetData = {}
	# ************* GET ORIGINAL TWEET DATA ************************
	if ('in_reply_to_status_id' in tweet._json):
		if str(tweet.in_reply_to_status_id) != 'None':
			try:
				# print("GETING ORIGINAL")
				if (api.validOriginalAPI()):
					# print("____ HERE ORIGINAL 1")
					api.currAPI().original.increment()
					originalTweetData = twitter.get_original_tweet_data(api.currAPI(), tweet.in_reply_to_status_id, analyzer)
					print("got original data for tweet. ", tweet.in_reply_to_status_id, api.currAPI().original.count)
				else:
					# print("____ HERE2")
					timeout = api.originalTimeout()
					print("sleeping for original" + str(timeout))
					time.sleep(timeout)
					api.reset()
			except:
				print("*******************Request failed for original tweet data *****************")

	# print(originalTweetData)
	# ************* GET TOP RETWEETS OF TWEET ************************
	topRetweets = []
	try:
		print("GET RETWEETS")
		if (api.validRetweetsAPI()):
			api.currAPI().retweets.increment()
			topRetweets = twitter.get_retweet_info(api.currAPI(), tweet.id_str, 5)
		else:
			timeout = api.retweetTimeout()
			print("sleeping for retweets " + str(timeout))
			time.sleep(timeout)
			api.reset()
	except:
		 print("******************* ERROR getting top retweets ****************")

	# # ******************** GET TWEET IMAGE ************************
	imageInfo = []
	tweetImages = []
	tweetColors = []
	try:
		imageInfo = twitter.get_tweet_image_info(tweet)
		tweetImages = imageInfo[0]
		tweetColors = imageInfo[1]
	except:
		print("*******************Request failed for tweet images *****************")

	# ******************** GET TWEET SENTEMENT ANALYSIS ************************
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

def analyse(screen_name, alltweets, apis):
	allData = {}
	analyzer = SentimentIntensityAnalyzer()

	for tweet in alltweets:
		#If the tweet is in response to another tweet, get that original tweet.
		data = processTweet(tweet, apis,analyzer)
		allData[tweet.id_str] = data
		for i in range(0,50):
			allData[tweet.id_str + str(i)] = data
		# print(data)
	return allData

def getAccountData(screen_name, getAll = True):
	 #convert to API objects instead of KEY objects
	keys = []
	keys.append(KEY( # Arun Soni api token meant for personal use
	"W2rzJn96XwhdUbOVPMxRARGoY",
	"Z0nBnpcZOvu569jkUVgBJhmyBBHuJb7c7RG1eHhTggkvyrp2ku",
	"200493359-Z07fyvzFppn7kqtvBMzoLlGmpob7Gtqm1rXFshBH",
	"nnj5ni1qtQj1awWfeo2JNWRi00btuukKiJOJD9zwsSNSH"))
	keys.append(KEY( # Neal Soni api token meant for personal use
	"devzpy79XxBxnHCZKO9NLpWdD",
	"jJ8oGnU4ULEdubsV9s7TIfrfhORo5U3Kf3CAY0vLHTcJco2rT3",
	"2573581272-d3PDuATbzta0XjCTTjaARdKuqCg8JmQRA8WvnjL",
	"CP3J1KhvXa1gc1zVddcX8tAqJbylywMTAOsKYCp6iJs2h"))
	keys.append(KEY( # Rando API token
	"muTI4PDvkLIbsUSg7Y5iMkptp",
	"sNCJrnABbHN4qzqGnZlsK27PiDhNPOcN8Tixc9h0RQiQsyXFQ4",
	"818209251474702337-oRXOrPvxio8ymKC5b3jsoJ2jrcBfcsX",
	"WMBaKqNqOKX7IGTUuAFHLUmbNxPpV0qdsuOwJXX58KCeC"))
	
	apis = [API(key.api) for key in keys]
	api = apiObject(apis)
	# get_all_followers(screen_name, getAll, apis) #uncomment if to get the followers

	# print(get_original_tweet_data(apis[0], "1076160984916656128"))

	alltweets = get_all_tweets(screen_name, getAll, api)
	allData = analyse(screen_name, alltweets, api)
	dataChunks = chunks(allData, 500)
	page = 0
	for item in dataChunks:
		firestore.saveTweetData(screen_name, item, page)
		page += 1
	# print(allData)

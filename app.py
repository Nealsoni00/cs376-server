from flask import Flask
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

app = Flask(__name__)

def get_user_information(new_tweet, screen_name):
    #get the infromation about the user from the first tweet. We can ignore it later on.
    name = new_tweet.user.name
    tweetsCount = new_tweet.user.statuses_count
    followersCount = new_tweet.user.followers_count
    friendsCount = new_tweet.user.friends_count
    likedCount = new_tweet.user.favourites_count
    createdDate = new_tweet.user.created_at
    profileURL = new_tweet.user.profile_image_url_https
    backgroundURL = new_tweet.user.profile_background_image_url_https
    userDescription = new_tweet.user.description

    print(screen_name + " name is " + str(new_tweet.user.name))
    print(screen_name + " has " + str(new_tweet.user.statuses_count) + " tweets" )
    print(screen_name + " has " + str(new_tweet.user.followers_count) + " followers" )
    print(screen_name + " has " + str(new_tweet.user.friends_count) + " friends" )
    print(screen_name + " has liked " + str(new_tweet.user.favourites_count) + " posts")
    print(screen_name + " has had a twitter since: " + str(new_tweet.user.created_at))
    print(screen_name + " background url: " + str(new_tweet.user.profile_background_image_url_https))
    print(screen_name + " profile photo url: " + str(new_tweet.user.profile_image_url_https))
    print(screen_name + " description " + str(new_tweet.user.description))

    print("\n\n\n\n\n________________________________________________\n\n\n\n\n")

    # with io.open(absolute_path_to_saveFiles + '%s_info.csv' % screen_name, 'w',  encoding="utf-8") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Name', 'Number of Tweets', 'Followers', 'Following', 'Number of Posts Liked', 'Been on twitter since', 'Profile URL', 'Background URL', 'Profile Description'])
    #     writer.writerow([name, tweetsCount, followersCount, friendsCount, likedCount, createdDate, profileURL, backgroundURL, userDescription])


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

	get_user_information(new_tweets[0], screen_name) #get and save user information from one tweet

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

@app.route('/')
def hello_world():
	getAccountData('elonmusk', True)
	return 'Hello, World!'
getAccountData('elonmusk', True)


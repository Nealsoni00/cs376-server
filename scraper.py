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

# Cleaning up the tweet to remove links, weird characters...
def clean_tweet(tweet):
    # Utility function to clean tweet text by removing links, special characters using simple regex statements.
    return re.sub(r"http\S+", "", tweet)
    #return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
# Getting the sentiment analysis for a single tweet
def get_tweet_sentiment(tweet):
        # create TextBlob object of passed tweet text
        analysis = TextBlob(clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


def get_tweet_image_info(tweet):
    tweetImages = []
    tweetColors = []
    if 'media' in tweet.entities:
        for image in tweet.entities['media']:
            url = image['media_url']
            tweetImages.append(url)

            if not os.path.isfile(absolute_path_to_images + tweet.id_str + '.png'): #if the file already exists, then dont download it again, just load the old one.
                resp = urllib.request.urlopen(url)
                img = np.asarray(bytearray(resp.read()), dtype="uint8")
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                cv2.imwrite(absolute_path_to_images + tweet.id_str + '.png',img)
                # cv2.imshow("Image", img)

            #Color Analysis:
            colors = colorgram.extract(absolute_path_to_images + tweet.id_str + '.png', 6);
            colors.sort(key=lambda c: c.hsl.h)
            colorsArray = []
            for color in colors:
                colorTemp = {}
                colorTemp["r"] = color.rgb.r
                colorTemp["g"] = color.rgb.g
                colorTemp["b"] = color.rgb.b
                colorsArray.append(colorTemp)
            tweetColors.append(colorsArray)
    return [tweetImages, tweetColors]

def get_original_tweet_data(apiObject, tweetID):
    api = apiObject.api

    originalTweetData = {}
    if str(tweetID) != 'None':
        apiObject.originalCount += 1
        # print("getting original tweet data for: ", tweetID)
        try:
            originalTweet = api.get_status(tweetID)
            print(originalTweet)
            imageInfo = []
            tweetImages = []
            tweetColors = []
            try:
                imageInfo = get_tweet_image_info(originalTweet, tweet_mode=extended)
                tweetImages = imageInfo[0]
                tweetColors = imageInfo[1]
            except:
                print("*******************Request failed for tweet images *****************")

            person = {}
            person["screen_name"] = str(originalTweet.user.screen_name)
            person["name"] = str(originalTweet.user.name)
            person["posts"] = int(originalTweet.user.statuses_count)
            person["followers"] = int(originalTweet.user.followers_count)
            person["friends"] = str(originalTweet.user.friends_count)
            person["verified"] = str(originalTweet.user.verified)
            person["discription"] = str(originalTweet.user.description)
            originalTweetData["likes"] = originalTweet.favorite_count
            originalTweetData["retweets"] = originalTweet.retweet_count
            originalTweetData["user"] = person
            originalTweetData["images"] = tweetImages
            originalTweetData["colors"] = tweetColors
            return originalTweetData
        except:
            print("error getting tweet with id: ", tweet.in_reply_to_status_id)
    else:
        print("here123")
        return {}
        # raise Exception('dont need to count this')


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
    userData = {'Name': name, 'Number of Tweets' : tweetsCount, 'Followers': followersCount, 'Following':friendsCount, 'Number of Posts Liked':likedCount, 'Been on twitter since': createdDate, 'Profile URL': profileURL, 'Background URL': backgroundURL, 'Profile Description':userDescription}
    firestore.saveHandleData(screen_name, userData);


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

def analize(screen_name, alltweets):
	currOriginalTweetsAPI = 0
    currTweetImagesAPI = 0
    currRetweetsAPI = 0

	for tweet in alltweets:
            #If the tweet is in response to another tweet, get that original tweet.
            originalTweetData = {}
            currAPINum = currOriginalTweetsAPI % len(apis)
            print(count, apis[currAPINum].originalCount)
            try:
                if str(tweet.in_reply_to_status_id) != 'None':
                    if  apis[currAPINum].originalCount == 0:
                        apis[currAPINum].originalStart = datetime.now()
                    elif apis[currAPINum].originalCount == 900:
                        print("\n\n\n                    SWITCHING APIS               \n\n\n")
                        currOriginalTweetsAPI += 1
                        currAPINum = currOriginalTweetsAPI % len(apis)
                        print("                  ", currAPINum, apis[currAPINum].originalCount , timedelta(minutes = 15) - (datetime.now() - apis[currAPINum].originalStart), "       ")

                        if apis[currAPINum].originalCount >= 900:
                            if timedelta(minutes = 15) > (datetime.now() - apis[currAPINum].originalStart):
                                print("pausing for ", timedelta(minutes = 15) - (datetime.now() - apis[currAPINum].originalStart))
                            while (timedelta(minutes = 15) > (datetime.now() - apis[currAPINum].originalStart)):
                                time.sleep(1) #just gotta wait untill that time is up
                            apis[currAPINum].originalCount = 0
                            apis[currAPINum].originalStart = datetime.now()

                    originalTweetData = get_original_tweet_data(apis[currAPINum], tweet.in_reply_to_status_id)
                    # apis[currApi % len(apis)].originalCount += 1
                    print("got original data for tweet. ", tweet.in_reply_to_status_id, apis[currAPINum].originalCount)
            except:
                # currApi += 1
                print("*******************Request failed for original tweet data *****************")
            count += 1

            # print(originalTweetData)
            #get the top retweets of the tweet.
            # topRetweets = []
            # try:
            #     topRetweets = get_retweet_info(apis[currTweetImagesAPI % len(apis)], tweet.id_str, 5)
            # except:
            #     currApi += 1
            #     print("******************* ERROR getting top retweets ****************")

            imageInfo = []
            tweetImages = []
            tweetColors = []
            try:
                imageInfo = get_tweet_image_info(tweet)
                tweetImages = imageInfo[0]
                tweetColors = imageInfo[1]
            except:
                print("*******************Request failed for tweet images *****************")


            tweettext = ""
            try: #if theres a long version of the tweet then use it.
                tweettext = tweet.full_text
            except AttributeError:
                tweettext =  tweet.text
            tweettext = clean_tweet(tweettext)


            # get tweet sentiment scores:
            score = analyzer.polarity_scores(tweettext)
            # print("SCORE: " + str(vs))

            print(              [tweet.id_str, tweet.created_at, tweet.favorite_count, tweet.retweet_count, tweet.in_reply_to_status_id, originalTweetData, tweetImages, tweetColors, tweettext, score])

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
	print(alltweets)

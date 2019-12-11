import tweepy #https://github.com/tweepy/tweepy
import io
import re
import requests
import numpy as np
import urllib
import cv2
import colorgram   #pip install colorgram.py
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import firestore

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
			print("Tweet has image!!!!!!")
			url = image['media_url']
			tweetImages.append(url)
			print("HERE4")
			# if not os.path.isfile(absolute_path_to_images + tweet.id_str + '.png'): #if the file already exists, then dont download it again, just load the old one.
			resp = urllib.request.urlopen(url)
			img = np.asarray(bytearray(resp.read()), dtype="uint8")
			img = cv2.imdecode(img, cv2.IMREAD_COLOR)
			print("HERE5")
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			im_pil = Image.fromarray(img)

			# cv2.imwrite(absolute_path_to_images + tweet.id_str + '.png',img)
				# cv2.imshow("Image", img)
			print("HERE6")
			#Color Analysis:
			colors = colorgram.extract(im_pil, 6);
			print("HERE7")
			print(colors)
			colors.sort(key=lambda c: c.hsl.h)
			colorsArray = []
			for color in colors:
				colorTemp = {}
				colorTemp["r"] = color.rgb.r
				colorTemp["g"] = color.rgb.g
				colorTemp["b"] = color.rgb.b
				colorsArray.append(colorTemp)
			tweetColors.append(colorsArray)
			print(colorsArray)
	return [tweetImages, tweetColors]

def get_original_tweet_data(apiObject, tweetID, analyzer):
	api = apiObject.api

	originalTweetData = {}
	if str(tweetID) != 'None':
		# apiObject.original.increment()
		# print("getting original tweet data for: ", tweetID)
		try:
			originalTweet = api.get_status(tweetID)
			# print(originalTweet)
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

			tweettext = ""
			try: #if theres a long version of the tweet then use it.
				tweettext = originalTweet.full_text
			except AttributeError:
				tweettext =  originalTweet.text
			originalTweetData["text"] = tweettext
			tweettext = clean_tweet(tweettext)
			# get tweet sentiment scores:
			score = analyzer.polarity_scores(tweettext)

			originalTweetData["score"] = score

			return originalTweetData
		except:
			print("error getting tweet with id: ", tweet.in_reply_to_status_id)
	else:
		print("here123")
		return {}
		# raise Exception('dont need to count this')

def get_retweet_info(apiObject, tweetID, num):
	# apiObject.api.original.increment()
    
    retweetInfo = {}
    print("getting retweets for " + str(tweetID))
    retweets = apiObject.api.retweets(tweetID, count=100)

    retweetsFormated = []
    for retweet in retweets:
        person = {}
        person["screen_name"] = str(retweet.user.screen_name)
        person["name"] = str(retweet.user.name)
        person["posts"] = int(retweet.user.statuses_count)
        person["followers"] = int(retweet.user.followers_count)
        person["friends"] = str(retweet.user.friends_count)
        person["verified"] = str(retweet.user.verified)
        person["discription"] = str(retweet.user.description)
        person["retweetID"] = str(retweet.id)
        retweetsFormated.append(person)
        # print(count, retweet.id, retweet.created_at, retweet.user.screen_name, "name:   " + str(retweet.user.name) + "     ", retweet.user.statuses_count, retweet.user.followers_count, retweet.user.friends_count, retweet.user.verified, retweet.user.description);
    retweetsFormated.sort(key=lambda x: x["followers"], reverse=True)
    return retweetsFormated[:num]

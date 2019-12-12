#!/usr/bin/env python

# Author: Neal Soni & Dylan Gleicher
# Used to process the twitter information stored in the folder with the passed in twitter handled. Ex.
# Run this using python3 TwitterPostProcessing <TwitterHandle>

import sys
import csv
import os
import ast
import json
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import math
from math import ceil, log10
from matplotlib import rcParams
from colorconverter import hsv2rgb, rgb2hsv
import graphs
import firestore
import imgur

rcParams.update({'figure.autolayout': True})

# Using Vader, this function returns an array with positive, neutral,
# and negative sentiment analysis percentages for each tweet we have
def getVaderAnalysis(screen_name):
	# Get all tweets possible with current API limitations
	allTweets = get_all_tweets(screen_name)

	count = 0
	negativeTweets = 0
	neutralTweets = 0
	positiveTweets = 0

	for tweet in allTweets:
		# Calling vader API to analyze the sentiment
		sentiment = ast.literal_eval(str(tweet["score"]))["compound"]

		if sentiment <= -0.05:
			negativeTweets += 1
		elif sentiment < 0.05:
			neutralTweets += 1
		else:
			positiveTweets += 1

		count += 1

	# Return the array
	vader = [(round((positiveTweets/count)*100,3)), (
		round((neutralTweets/count)*100,3)), (
		round((negativeTweets/count)*100,3))]
	return vader


def step (rgb, repetitions=1):
	r = rgb[0]
	g = rgb[1]
	b = rgb[2]

	lum = math.sqrt( .241 * r + .691 * g + .068 * b )

	h, s, v = rgb2hsv(r,g,b)

	h2 = int(h * repetitions)
	lum2 = int(lum * repetitions)
	v2 = int(v * repetitions)

	if h2 % 2 == 1:
		v2 = repetitions - v2
		lum = repetitions - lum

	return (h2, lum, v2)

def chunkIt(seq, num):
	avg = len(seq) / float(num)
	out = []
	last = 0.0

	while last < len(seq):
		out.append(seq[int(last):int(last + avg)])
		last += avg

	return out
def evalSentement(score):
	try:
		negativeTweets = 0
		neutralTweets = 0
		positiveTweets = 0
		sentiment = ast.literal_eval(str(score))["compound"]
		if sentiment <= -0.05:
			negativeTweets += 1
		elif sentiment < 0.05:
			neutralTweets += 1
		else:
			positiveTweets += 1
		return negativeTweets, neutralTweets, positiveTweets
	except:
		return 0, 0, 0

def postProcess(screen_name, allTweets, userinfo):
	outputJSON = {}

	count = 0
	likes = []
	likesWithImages  = []
	likesForRetweet  = []
	likesForOriginal = []

	hashtags = []
	retweets = []
	tweetRespondedTo = []
	colors = []
	tweetRespondedToUsers = {}
	responseCount = 0
	tweetsWithImages = 0

	tweetsWithNoLikes = 0

	negativeTweets = 0
	neutralTweets = 0
	positiveTweets = 0
	tweetsArray = []
	for i in allTweets:
		tweet = allTweets[i];
		tweetsArray.append(tweet)
		# print(count, tweet)
		likes.append(int(tweet["likes"]))
		retweets.append(int(tweet["retweets"]))
		# print(tweet["originalTweetData"])

		#get who the user responds to:
		originalTweet =  ast.literal_eval(str(tweet["originalTweetData"]))
		tweetRespondedTo.append(originalTweet)
		try:
			original_screen_name = originalTweet["user"]["screen_name"]
			if original_screen_name in tweetRespondedToUsers.keys():
				tweetRespondedToUsers[original_screen_name][0] += 1
				tweetRespondedToUsers[original_screen_name][1].append(originalTweet)
			else:
				tweetRespondedToUsers[original_screen_name] = [1, [originalTweet]]

			if originalTweet["images"] != '[]':
				tweetsWithImages += 1
				imagesColors = originalTweet["colors"]
				likesWithImages.append(int(tweet["likes"]))
				for color in imagesColors:
					colors.append(np.array((int(color['r']), int(color['g']), int(color['b']))))
			# if originalTweet["score"] != None:
				# print("original")
				# negativeTweets, neutralTweets, positiveTweets += evalSentement(tweet["score"])
		except:
			pass

		if tweet["responseTo"] != '':
			likesForRetweet.append(int(tweet["likes"]))
			responseCount += 1
		else:
			likesForOriginal.append(int(tweet["likes"]))
		if tweet["images"] != '[]':
			tweetsWithImages += 1
			likesWithImages.append(int(tweet["likes"]))
			imagesColors = ast.literal_eval(str(tweet["colors"]))
			for color in imagesColors:
				colors.append(np.array((int(color['r']), int(color['g']), int(color['b']))))
		
		neg, neut, pos = evalSentement(tweet["score"])
		positiveTweets += pos
		neutralTweets += neut
		negativeTweets += neg
		
		if int(tweet["likes"]) == 0:
			tweetsWithNoLikes += 1
		count += 1
		if tweet['hashtags']:
			for hashtag in tweet['hashtags']:
				hashtags.append(hashtag)

	print("count of colors: ", len(colors))
	outputJSON["colorCount"] = len(colors)

	# imageName = createImagePallete(colors)
	# outputJSON["colorImage"] = imageName
	outputJSON['hashtags'] = hashtags

	print("there are " + str(count) + " tweets")
	outputJSON["tweetCount"] = str(count)


	print("(% Positive, % Neutral, % Negative): (", round(positiveTweets/count,5), round(neutralTweets/count, 5), round(negativeTweets/count, 5), ") tweets")
	sentimentRatio =   {"positiveP" : round(positiveTweets/count,5),
						"neutralP"  : round(neutralTweets/count, 5),
						"negativeP" : round(negativeTweets/count, 5),
						"positiveC" : round(positiveTweets,5),
						"neutralC"  : round(neutralTweets, 5),
						"negativeC" : round(negativeTweets, 5)}
	outputJSON["sentiment"] = sentimentRatio


	tweetsArray.sort(key=lambda x: int(x["likes"]), reverse=True)
	topFiveTweets = tweetsArray[:5]
	outputJSON["topFiveTweets"] = topFiveTweets
	print(topFiveTweets)


	likes.sort()
	retweets.sort()
	likesWithImages.sort()
	outputJSON['likes'] = likes
	outputJSON['retweets'] = retweets
	outputJSON['likes_with_images'] = likesWithImages

	# ************** LIKE DISTRIBUATION HISTOGRAMS ****************

	likes_histogram = graphs.makeHistogram("likes_histogram", likes, "likes per post", "# of posts in range", "Histogram of likes for "+screen_name+" tweets")
	likes_with_images_histogram = graphs.makeHistogram("likes_with_images_histogram", likesWithImages, "likes per post with image", "# of posts in range", "Histogram of likes for "+screen_name+"'s tweets with images")
	likes_for_retweets_histogram = graphs.makeHistogram("likes_for_retweets_histogram", likesForRetweet, "likes per retweet post", "# of posts in range", "Histogram of likes for tweets "+screen_name+" retweets")
	likes_for_original_histogram = graphs.makeHistogram("likes_for_original_histogram", likesForOriginal, "likes per original post", "# of posts in range", "Histogram of likes for "+screen_name+"'s original tweets")

	outputJSON['histograms'] = {
		"likes_histogram": {'graph': likes_histogram, 'data': likes},
		"likes_with_images_histogram": {'graph': likes_with_images_histogram, 'data': likesWithImages},
		"likes_for_retweets_histogram": {'graph': likes_for_retweets_histogram, 'data': likesForRetweet},
		"likes_for_original_histogram": {'graph': likes_for_original_histogram, 'data': likesForOriginal}
		}

	# *************** People Responded To **************************
	# By Count:
	tweetRespondedToUsersKeys = list(tweetRespondedToUsers.keys())
	tweetRespondedToUsersKeys.sort(key=lambda x: tweetRespondedToUsers[x][0], reverse=True)
	topFiveRespondingTo = tweetRespondedToUsersKeys[:5]
	topFiveReversed = topFiveRespondingTo[::-1]
	print("top five people responded to: ", topFiveRespondingTo)
	outputJSON["top_five_responded_to"] = topFiveRespondingTo

	responded_most = graphs.createHorizontalSingleBarGraph(
		"responded_most",
		topFiveReversed,
		[tweetRespondedToUsers[x][0] for x in topFiveReversed],
		'Responses (#)',
		'Account (user name)',
		"Top 5 Accounts Responded To")
	
	# By Popularity: 
	tweetRespondedToUsersKeys = list(tweetRespondedToUsers.keys())
	tweetRespondedToUsersKeys.sort(key=lambda x: int(tweetRespondedToUsers[x][1][0]["user"]["followers"]), reverse=True)
	topFiveMostPopularRespondingTo = tweetRespondedToUsersKeys[:5]
	topFivePopularReversed = topFiveMostPopularRespondingTo[::-1]
	outputJSON["top_five_popular_responded_to"] = topFivePopularReversed
	print("Top five most popular people responded to: ", topFiveMostPopularRespondingTo)
	responded_popular = graphs.createHorizontalSingleBarGraph(
		"responded_popular",
		topFivePopularReversed,
		[int(tweetRespondedToUsers[x][1][0]["user"]["followers"]) for x in topFivePopularReversed],
		'Account Followers (#)',
		'Account (user name)',
		"Top 5 Most Popular Accounts Responded To")

	outputJSON['graphs'] = {
		"top_five_responded_to_graph": {'graph': responded_most, 'labels': topFiveReversed, 'data': [tweetRespondedToUsers[x][0] for x in topFiveReversed]},
		"top_five_most_popular_responded_to_graph": {'graph': responded_popular, 'labels': topFivePopularReversed, 'data': [int(tweetRespondedToUsers[x][1][0]["user"]["followers"]) for x in topFivePopularReversed]}
	}

	# ********** No Likes ***********
	no_likes_percent = round(tweetsWithNoLikes/count, 5)
	no_likes_count = round(tweetsWithNoLikes, 5)

	print("% tweets with no likes:", no_likes_percent)
	outputJSON["no_likes_percent"] = no_likes_percent
	outputJSON["no_likes_count"] = no_likes_count

	tweetsArray.sort(key=lambda x: int(x["likes"]), reverse=True)
	fivePercent = int(count*0.05)
	topFivePercentofTweets = tweetsArray[:fivePercent]
	# print(topFiveTweets["image"])
	countOfImagesInTopFivePercent = 0
	for tweet in topFivePercentofTweets:
		if tweet["images"] != '[]':
			countOfImagesInTopFivePercent += 1

	top_5_percent_have_images = round(countOfImagesInTopFivePercent/(fivePercent + 1), 5)
	outputJSON['top_5_percent_have_images'] = top_5_percent_have_images
	print("out of the top 5% of the tweets,",top_5_percent_have_images, "had images")
	

	median_likes = round(likes[int(count/2)])
	median_likes_with_images = round(likesWithImages[int(tweetsWithImages/2)])
	median_retweets = round(retweets[int(count/2)])
	outputJSON['median_likes'] = median_likes
	outputJSON['median_likes_with_images'] = median_likes_with_images
	outputJSON['median_retweets'] = median_retweets
	print("Median likes: ", median_likes)
	print("Median likes with Images:", median_likes_with_images)
	print("Median retweets: ",median_retweets)
	
	percent_posts_w_img =  round(tweetsWithImages/(count + 1),5)
	print("% of posts with images: ", percent_posts_w_img)
	outputJSON['percent_posts_w_img'] = percent_posts_w_img

	responded_to_v_self_posted = round(responseCount/(count - responseCount + 1),5)
	print("(responded tweets : self posted tweets) ratio: ",responded_to_v_self_posted )
	outputJSON['responded_to_v_self_posted'] = responded_to_v_self_posted

	print(outputJSON)
	return outputJSON

def getAccountInfo(screen_name):
	print("Processing Account: ", screen_name)
	# screen_name = screen_name.lower()
	allTweets = firestore.getTweets(screen_name)
	userinfo = firestore.getInfo(screen_name)
	data = postProcess(screen_name, allTweets, userinfo)
	firestore.saveProcessedData(screen_name, data)

def processAllAccounts():
	handles = firestore.getAllHandles()
	print("Processing All Handles: ", handles)
	for handle in handles:
		getAccountInfo(handle)
def Remove(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 

def generateGraph():
	handles = firestore.getAllHandles()
	nodesArray = []
	nodesMap = []
	edges = []
	nodesCount = 0

	def addNode(edge, count):
		if not edge in nodesArray or not edge.lower() in nodesArray:
			nodesArray.append(edge.lower())
			nodesMap.append({'id': edge.lower(), 'name': edge.lower()})
			count += 1
		return count
	
	for handle in handles:
		print("HANDLE: ", handle)
		# handleID = nodesCount
		nodesCount = addNode(handle, nodesCount)
		processedData = firestore.getProcessedData(handle)
		try: 
			connectedTo = processedData['top_five_responded_to']
			for edge in connectedTo:
				nodesCount = addNode(edge, nodesCount)
				edges.append({'sid': handle.lower(), 'tid': edge.lower(), '_color': 'red' })
		except:
			print("CAN't get data for handle: ", handle)
	nodesMap = Remove(nodesMap)
	firestore.saveGraph({'nodes': nodesMap, 'edges': edges})
	print(edges)
	print(nodesMap)
	return nodesArray

def unscrapedHandles():
	handles = firestore.getAllHandles()
	nodesArray = generateGraph()
	unprocessedHandles = []
	for handle in nodesArray:
		if not handle in handles and not handle in unprocessedHandles:
			unprocessedHandles.append(handle)
	return unprocessedHandles




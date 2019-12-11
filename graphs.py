import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import math
from math import ceil, log10
from matplotlib import rcParams
from colorconverter import hsv2rgb, rgb2hsv
from graphs import *
import firestore
import imgur

def createImagePallete(colors):
	# fig, ax = plt.subplots()
	rows = int(len(colors)/100) if len(colors) > 100 else 8
	pallete = sorted(colors, key=lambda rgb : step(rgb,rows))

	# rows = int(len(pallete)/100) if len(pallete) > 100 else 8
	pallete = pallete[:len(pallete)-len(pallete)%rows]

	palette = np.array(chunkIt(pallete, rows))
	# indices = np.random.randint(0, len(palette), size=(4, 6))
	# print(palette)
	plt.imshow(palette)

	ax = plt.subplot(111)
	ax.spines["top"].set_visible(False)
	ax.spines["right"].set_visible(False)
	ax.spines["bottom"].set_visible(False)
	ax.spines["left"].set_visible(False)
	plt.title("Color Pallete for "+ screen_name, fontsize=18)
	ymin, ymax = ax.get_ylim()
	print(ymax)
	plt.text(0, -1 * ymax/10, "Data source: www.twitter.com", fontsize=10)
	plt.axis('off')
	plt.tight_layout()
	# plt.colorbar()
	photoName = screen_name + "_pallete" + '.pdf'
	# plt.savefig(photoName)
	html = imgur.upload(plt.gcf(), photoName)
	return photoName
	# plt.show()

def createHorizontalSingleBarGraph(name, x, y, x_axis, y_axis, title):
	# fig, ax = plt.subplots()

	plt.clf()
	y_pos = np.arange(len(x))
	ax = plt.subplot(111)
	ax.spines["top"].set_visible(False)
	ax.spines["right"].set_visible(False)
	arr = plt.barh(y_pos, y, align='center', alpha=0.5)
	plt.yticks(y_pos, x, fontsize=14)
	plt.xticks(fontsize=14)
	plt.xlabel(x_axis, fontsize=16)
	plt.ylabel(y_axis, fontsize=16)
	plt.title(title, fontsize=22)
	for i, v in enumerate(y):
		ax.text(v, i, str("{:,}".format(v)),  fontweight='bold')
	plt.text(0, -1.25, "Data source: www.twitter.com"
			 "", fontsize=10)
	plt.tight_layout()

	# plt.savefig(path + screen_name + "_" + name + '.pdf')
	html = imgur.upload(plt.gcf(), title)
	return html
	# return screen_name + name
	# plt.show()
	# plt.savefig(title + '.pdf')

def createHorizontalDoubleBarGraph(name, x, y1, y2, x_axis, y_axis, title):

	fig, ax1 = plt.subplots()

	color = 'tab:red'
	y_pos = np.arange(len(x))
	ax1.set_ylabel('time (s)')
	ax1.set_xlabel('exp', color=color)
	ax1.barh(y_pos, y1, align='center', color=color)
	ax1.tick_params(axis='y', labelcolor=color)

	ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

	color = 'tab:blue'
	ax2.set_xlabel('sin', color=color)  # we already handled the x-label with ax1
	ax2.barh(y_pos, y2, align='center', color=color)
	ax2.tick_params(axis='y', labelcolor=color)

	fig.tight_layout()  # otherwise the right y-label is slightly clipped
	plt.show()

	# plt.savefig(path + name + '.pdf')
	html = imgur.upload(plt, photoName)
	return html


def makeHistogram(name, data, x_axis, y_axis, title):
	# fig, ax = plt.subplots()

	plt.clf()
	plt.figure(figsize=(12, 9))
	ax = plt.subplot(111)
	ax.spines["top"].set_visible(False)
	ax.spines["right"].set_visible(False)
	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()
	plt.xticks(fontsize=14)
	plt.yticks(fontsize=14)
	plt.xlabel(x_axis, fontsize=16)
	plt.ylabel(y_axis, fontsize=16)
	plt.title(title,   fontsize=22)
	bins = 50

	arr = plt.hist(list(data),
			  alpha=0.5, bins=50)
	ymin, ymax = ax.get_ylim()
	for i in range(bins):
		if arr[0][i] != 0:
			plt.text(arr[1][i],arr[0][i]+ymax/90,str("{:,}".format(int(arr[0][i]))),fontweight='bold')

	plt.text(0, -1 * ymax/10, "Data source: www.twitter.com", fontsize=10)
	plt.tight_layout()
	box_inches="tight" #removes all the extra whitespace on the edges of your plot.
	# print(path + screen_name + "_" + name + '.pdf')
	
	# plt.savefig(name + '.pdf')
	html = imgur.upload(plt.gcf(), title)
	return html
	# plt.show()
	# return name + '.pdf'

	# computingScores(userinfo, getVaderAnalysis(screen_name))

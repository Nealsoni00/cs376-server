import process
import scraper
import sys

if __name__ == '__main__':
    #pass in the username of the account you want to download
    # 
	# for i in range(1,len(sys.argv)):
	# 	screen_name = sys.argv[i]
	# 	# try:
	# 	allData = scraper.getAccountData(screen_name, True)
		# except:
		# 	print("*********** ERROR SCRAPING DATA FOR: ", screen_name, "*****************")
	# try:
	# processed = process.processAllAccounts()
	process.generateGraph()
	# except:
	# 	pass
import process
import scraper
import sys

# Comment out code if you don't want to make this take forever. 
if __name__ == '__main__':
    #pass in the usernames of the account you want to download
	
	scrape = False
	processs = True
	children = False 
	
	if scrape:
		for i in range(1,len(sys.argv)):
			screen_name = sys.argv[i]
			try: 							# MAKE THIS (screen_name, False, 200) IF YOU WANT IT TO SCRAPE FASTER
				allData = scraper.getAccountData(screen_name, True, 1000)
			except:
				print("*********** ERROR SCRAPING DATA FOR: ", screen_name, "*****************")

	if process: 
		# Process the data after it's been scraped 
		processed = process.processAllAccounts()
		graph = process.generateGraph()
		
	if children: 
		unscrapedHandles = process.unscrapedHandles()
		# get children of account. 
		for handle in unscrapedHandles:
			try:
				allData = scraper.getAccountData(handle, False, 1000) # smaller so it doesn't take too long
			except:
				print("************** ERROR SCRAPING DATA FOR: ", screen_name, "*****************")
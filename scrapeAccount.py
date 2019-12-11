import process
import scraper
import sys

if __name__ == '__main__':
    #pass in the username of the account you want to download
    # 
   	for i in range(1,len(sys.argv)):
   		process.getAccountInfo(sys.argv[i])
   	# 	allData = scraper.getAccountData(sys.argv[i], True)
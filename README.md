# cs376-server

> CS376 Final Web Project Server & Twitter Scraper
> By Dylan Gleicher and Neal Soni

## Python Web Scraper

### Setup

There are three parts to the web scraper, (1) scraping and (2) post-processing (3) children manipulation. To initialize both of them to work, run the following command:

```bash
$ pip3 install -r reqirements.txt
```

The three parts can be enabled and disabled in the "scrapeAccount.py" script:
```python
	scrape = True # Disable to stop scraping from occuring
    processs = True # Disable to stop post-porcessing from occuring
    children = True # Disable to stop fetching children
```

The script is run using the following command: 
```bash
$ python3 scrapeAccount [twitter_handle]
```

### Scraping

This gets data from twitter, and inputs it into the firebase firestore database. Due to firestore rate limits, I store them at 450 tweets per page and around 6 pages per user. 
Note: Due to rate limits this script can take a long time to run. We are working to improve it's efficiency.

### Post Processing

This script is used to process the twitter information stored in the folder with the passed in twitter handled. This analyses overall tweet sentiment, common themes in the text, common colors and pallete used in the images, creates histograms and bar graphs detailing who the handle most responds to, how many tweets post, what likes they get, frequency, who they retweet, and more... All post processed data is stored in the same folder under the user's twitter handle name.

This step also generates the graph you see on the root dashboard. 

### Children Populating

This is where we scrape for the children nodes of the parent. Run post-processing again after populating the children to ensure that the data is processed correclty for the client to display. 

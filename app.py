from flask import Flask
import numpy as np
import pandas as pd
import process
import scraper
app = Flask(__name__)

@app.route('/')
def hello_world():
	allData = scraper.getAccountData('tesla', True)
	# process.getAccountInfo('elonmusk')
	return 'Hello, World!'
	


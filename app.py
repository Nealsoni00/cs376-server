from flask import Flask
import numpy as np
import pandas as pd
import process
import scraper
app = Flask(__name__)

@app.route('/')
def hello_world():
	# allData = scraper.getAccountData('elonmusk', False)
	process.getAccountInfo('elonmusk')
	return 'Hello, World!'
	


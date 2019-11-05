from flask import Flask
import numpy as np
import pandas as pd

import scraper
app = Flask(__name__)

@app.route('/')
def hello_world():
	scraper.getAccountData('elonmusk', False)
	return 'Hello, World!'
	


import os
import json
from flask import Flask, flash, request, redirect, url_for, session, send_file
import zipfile
from werkzeug.utils import secure_filename
import logging
import base64
import pandas as pd
from driver import *
import logging
import sys

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('Opened Log')

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
logging.basicConfig(level=logging.DEBUG)

driver = Driver()

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login', methods = ['POST'])
def store_login():
	user = request.form.get("user")
	pw = request.form.get("pw")
	driver.store_login(user, pw)
	return "Stored"

@app.route('/get_profiles', methods = ['POST'])
def scrape_profile_links():
	lead_list_link = request.form.get("list_link")
	print(lead_list_link)
	driver.get_profile_urls(lead_list_link)
	profile_list = driver.get_profile_list()
	print("REACHED", profile_list)
	textfile = open("./data/test_output/profile_list.txt", "w")
	for prof in profile_list:
	    textfile.write(prof + "\n")
	textfile.close()

	try:
		return send_file("../data/test_output/profile_list.txt", attachment_filename='profile_list.txt')
	except Exception as e:
		return str(e)

@app.route('/scrape_profiles', methods = ['POST'])
def scrape_profiles():
	profile_idx = int(request.form['profile_idx'])
	ROCKET_KEY = str(request.form['ROCKET_KEY'])
	VERIFY_KEY = str(request.form['VERIFY_KEY'])
	driver.store_creds(ROCKET_KEY, VERIFY_KEY)
	print("IDX", profile_idx)
	print(request.files)
	profile_data_raw = request.files['profile_list']
	file_data = profile_data_raw.read().decode("latin-1")
	profile_urls = [] 
	for item in file_data.split("\n"):
		if item != "":
			profile_urls.append(item)
	result = ""
	try: 
		result = driver.scrape_profiles(profile_urls, profile_idx)
	except:
		result = "Error"
	return result


@app.route('/download_profiles', methods = ['GET'])
def download_profiles():
	profile_data = driver.get_profile_data()
	
	profiles_df = pd.DataFrame.from_dict(profile_data)
	profiles_df = profiles_df.drop_duplicates(subset='Name', keep="first")
	profiles_df.to_excel("./data/test_output/profile_data.xlsx", index = False)
	
	try:
		print(sys.path)
		return send_file("../data/test_output/profile_data.xlsx", attachment_filename = "profile_data.xlsx", as_attachment = True)
	except Exception as e:
		return str(e)


app.secret_key = os.urandom(24)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5002, debug = True)
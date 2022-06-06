import os
import json
from flask import Flask, flash, request, redirect, url_for, session, send_file
import zipfile
from werkzeug.utils import secure_filename
import logging
import base64
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import time
import re
import pandas as pd

import json
import requests
import nltk
import flask
from flask import request

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('Opened Log')

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

class Driver:
	def __init__(self):
		self.user = None
		self.pw = None
		self.URL_LIST_PATH = None
		self.sel_driver = None
		self.profile_list = []
		self.profiles_data = {}
		self.profiles_data["Name"] = []
		self.profiles_data["# Years in Current Role"] = []
		self.profiles_data["Linkedin URL"] = []
		self.profiles_data["Email"] = []
		self.profiles_data["Email Verified? Yes/No"] = []
		self.profiles_data["Undergraduate College / University"] = []
		self.profiles_data["Location (city) of individual"] = []
		self.profiles_data["Location (state) of individual"] = []
		self.profiles_data["Current Company"] = []
		self.profiles_data["Current Company URL"] = []
		self.profiles_data["# LinkedIn Employees at Current Company"] = []
		self.profiles_data["Company industry category"] = []
		self.profiles_data["Location (city) of Company"] = []
		self.profiles_data["Location (state) of Company"] = []

		self.ROCKET_KEY = None
		self.VERIFY_KEY = None
	
	def store_login(self, user, pw):
		"""Store login creds"""
		self.user = user
		self.pw = pw

	def login(self):
		"""Login to Sales Navigator. Uses the stored login (user, pw) with selenium. """
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--start-maximized")
		chrome_options.add_argument("--disable-gpu")
		chrome_options.add_argument("--no-sandbox")
		##chrome_options.add_argument('--headless')
		chrome_options.add_argument("--disable-notifications")
		chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
		chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
		chrome_options.add_experimental_option('useAutomationExtension', False)
		#driver = webdriver.Chrome(options=chrome_options,executable_path="/usr/bin/chromedriver")
		driver = webdriver.Chrome(options=chrome_options,executable_path="./chromedriver")
		driver.get("https://www.linkedin.com/sales/login")
		time.sleep(1)
		WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,".authentication-iframe")))
		driver.find_element_by_css_selector('#username').send_keys(self.user)
		driver.find_element_by_css_selector('#password').send_keys(self.pw)
		button = driver.find_element_by_css_selector('.login__form_action_container>button')
		print(button)
		button.click()
		print("LOGGED IN")
		time.sleep(10)
		self.sel_driver = driver
		return 'Logged In!'

	def get_login_creds(self):
		return self.user, self.pw

	def get_profile_urls(self, list_link):
		"""Scrape profile urls from lead list.
		Input: List_Link - url to saved lead list.
		Output: profile_urls - saved profile urls """
		print(self.login())
		print("Parsing URLs")
		self.list_link = list_link
		print(self.list_link)
		self.sel_driver.get(list_link)
		time.sleep(5)
		idx = 2
		self.profile_urls = []
		buttons = []
		while idx <= 150:

			#self.sel_driver.execute_script("window.scrollTo(0, document.body.scrollHeight*100);")
			y = 1000
			for timer in range(0,7):
				self.sel_driver.execute_script("document.getElementById('search-results-container').scrollTop = "+str(y))
				y += 1000 
				time.sleep(1)

			divs = self.sel_driver.find_elements_by_class_name('artdeco-entity-lockup__title')

			for div in divs:
				url = div.find_element_by_css_selector('a').get_attribute('href')
				self.profile_urls.append(url)
				print(url, idx)

			button = None
			
			try:
				button = self.sel_driver.find_element_by_xpath('//li[@data-test-pagination-page-btn="{}"]/button'.format(idx))
			except:
				break

			button.click()


			time.sleep(3)
			print("# Profiles", len(self.profile_urls))
			idx += 1
		
		print("Total # Profiles to Scrape", len(self.profile_urls))
		self.sel_driver.close()
		return "Finished"

	def scrape_profiles(self, profile_urls, profile_idx):
		"""Scrape profile-level data (user info, company info). 
		Input: profile_urls (output of get_profile_urls)
		Output: profiles_data - pandas df of scraped profile data"""
		self.login()
		print("URLS:", profile_urls[0])
		for idx, prof_url in enumerate(profile_urls):
			print("INDEX", idx)
			if idx < profile_idx:
				continue
			if idx >= (profile_idx + 250):
				break
			print("PROFILE {}".format(idx))
			self.sel_driver.get(prof_url)
			time.sleep(3)
			print(prof_url)
			name_div = None
			try:
				name_div = self.sel_driver.find_element_by_xpath('.//span[@class = "profile-topcard-person-entity__name t-24 t-black t-bold"]')
			except:
				print("couldn't find!")
				break #Profile viewing limit exceeded
			name = name_div.text
			print("Name", name)

			time.sleep(1)
			title_div = self.sel_driver.find_element_by_xpath('.//span[@class = "profile-topcard__summary-position-title"]')
			title = title_div.text
			print("Title", title)

			time_div = self.sel_driver.find_element_by_xpath('.//span[@class = "profile-topcard__time-period-bullet"]')
			num_years = time_div.text
			print("# Years", num_years)

			location_div = self.sel_driver.find_element_by_xpath('.//div[@class = "profile-topcard__location-data inline t-14 t-black--light mr5"]')
			prof_loc = location_div.text
			prof_city, prof_state = "", ""
			if "," in prof_loc:
				text = prof_loc.split(",")
				prof_city = text[0]
				prof_state = text[1]

			print("Profile Location", prof_city + "," + prof_state)

			#Get Education Info
			time.sleep(1)
			edu_div = self.sel_driver.find_elements_by_xpath('.//li[@class = "profile-education display-flex align-items-flex-start"]')
			undergrad_text = ""
			for item in edu_div:
				raw_text = item.text.split("\n")
				if len(raw_text) <= 3:
					continue
				uni_text = raw_text[0]
				degree_text = raw_text[2]
				if "Bachelor" in degree_text or \
					("BA" in degree_text and "MBA" not in degree_text) \
					or ("B.A." in degree_text and "M.B.A." not in degree_text) \
					or "BS" in degree_text or "B.S." in degree_text \
					or "AB" in degree_text or "A.B." in degree_text \
					or "B.E." in degree_text or "E.B." in degree_text:
					undergrad_text = uni_text
			print("Undergrad", undergrad_text)

			#Get Company-Level Info
			company_div = None
			company_link, company_text = "", ""
			
			try:
				company_div = self.sel_driver.find_element_by_xpath('.//a[@class = "li-i18n-linkto inverse-link-on-a-light-background t-14 t-black t-bold"]')
				company_link = company_div.get_attribute('href')
				company_text = company_div.text
			except:
				company_div = self.sel_driver.find_element_by_xpath('.//span[@class = "t-14 t-black t-bold"]')
				company_text = company_div.text
			industry, num_employees, comp_city, comp_state = "","","",""
			print("COMPANY LINK", company_text, company_link)
			if company_link != "":
				self.sel_driver.get(company_link)
				time.sleep(2.5)
				industry_div = self.sel_driver.find_element_by_xpath('.//div[@class = "t-14"]')
				industry_raw = industry_div.text
				print(industry_raw)
				industry = ' '.join(industry_raw.split(" ")[0:2])
				num_employees_div = self.sel_driver.find_element_by_xpath('.//a[@class = "ember-view link-without-visited-and-hover-state"]')
				is_thousand = "K" in num_employees_div.text

				num_employees = float(re.sub("[^\d.]+", "", num_employees_div.text))
				if is_thousand: num_employees *= 1000
				num_employees = int(num_employees)
				
				print("Company Info", company_link + " " + company_text + " "
				+ industry + " " + str(num_employees) + " " + comp_city + ", " + comp_state)

				comp_loc_div = self.sel_driver.find_element_by_xpath('.//div[@class = "t-12 t-black--light"]')
				comp_loc = comp_loc_div.text
				comp_city, comp_state = "", ""
				if "," in comp_loc:
					text = comp_loc.split(",")
					comp_city = text[0]
					comp_state = text[1]
				
				print("Company Info", company_link + " " + company_text + " "
				+ industry + " " + str(num_employees) + " " + comp_city + ", " + comp_state)


			print("Company Info", company_link + " " + company_text + " "
				+ industry + " " + str(num_employees) + " " + comp_city + ", " + comp_state)

			self.profiles_data["Name"].append(name)
			self.profiles_data["# Years in Current Role"].append(num_years)
			self.profiles_data["Linkedin URL"].append(prof_url)
			self.profiles_data["Email"].append("")
			self.profiles_data["Email Verified? Yes/No"].append("No")
			self.profiles_data["Undergraduate College / University"].append(undergrad_text)
			if prof_city and prof_state:
				self.profiles_data["Location (city) of individual"].append(prof_city)
				self.profiles_data["Location (state) of individual"].append(prof_state)
			else:
				self.profiles_data["Location (city) of individual"].append(prof_loc)
				self.profiles_data["Location (state) of individual"].append(prof_loc)

			self.profiles_data["Current Company"].append(company_text)
			self.profiles_data["Current Company URL"].append(company_link)
			self.profiles_data["# LinkedIn Employees at Current Company"].append(num_employees)
			self.profiles_data["Company industry category"].append(industry)
			if comp_city and comp_state:
				self.profiles_data["Location (city) of Company"].append(comp_city)
				self.profiles_data["Location (state) of Company"].append(comp_state)
			else:
				self.profiles_data["Location (city) of Company"].append(comp_loc)
				self.profiles_data["Location (state) of Company"].append(comp_loc)
		self.sel_driver.close()
		self.verify_emails()
		return "Success"

	def store_creds(self, ROCKET_KEY, VERIFY_KEY):
		self.ROCKET_KEY = ROCKET_KEY
		self.VERIFY_KEY = VERIFY_KEY

	def verify_emails(self):
		"""Email Lookup + Verification using RocketReach and VerifyEmail. 
		Output: profiles_data - pandas df of updated profile data with email & verification status"""
		print("Verifying")
		names = self.profiles_data["Name"]
		companies = self.profiles_data["Current Company"]
		#Rocket Reach - Email Lookup
		rocket_url = "https://api.rocketreach.co/v2/api/lookupProfile"
		rocket_headers = {"Api-Key": self.ROCKET_KEY}

		emails, verifies = [], []
		for idx, (name, company) in enumerate(zip(names, companies)):
			#Lookup Email
			rock_r = requests.get(rocket_url, data = {"name":name, "current_employer":company}, headers = rocket_headers)
			data = rock_r.json()
			email = ""
			if 'detail' not in data:
				email = data["current_work_email"]

			verified = "No"
			if email != "":
				verify_url = "https://app.verify-email.org/api/v1/{0}/verify/{1}".format(self.VERIFY_KEY, email)
				r = requests.get(verify_url)
				data = r.json()
				if data['status'] == 1:
					verified = "Yes"
			
			print(idx, name, company, email, verified)
			emails.append(email)
			verifies.append(verified)

		self.profiles_data["Email"] = emails
		self.profiles_data["Email Verified? Yes/No"] = verifies

		return "Success"


	def get_profile_data(self):
		return self.profiles_data

	def get_profile_list(self):
		return self.profile_urls


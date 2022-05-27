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

#Hummingbird usage
#python TestScraper.py config.txt "LINK" ../data/hummingbird_output/profile_list.txt ../data/hummingbird_output/profiles.xlsx 0 ../data/hummingbird_output/profiles_data.txt 

#Usage - End to End
# python TestScraper.py config.txt "https://www.linkedin.com/sales/search/REDACTED" output/profile_list.txt output/profiles.xlsx 0 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY

#Usage - Just Profile Parsing
# python TestScraper.py config.txt "None" output/profile_list.txt output/profiles.xlsx 51 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY

#Usage - Just Email Lookup/Verification
# python TestScraper.py config.txt "None" output/profile_list.txt output/profiles.xlsx -1 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY

driver = None
profile_urls = None


def main():
	args = sys.argv[1:]
	print(len(args))
	CONFIG_PATH = args[0]
	LIST_LINK = args[1]
	PROFILE_PATH = args[2]
	XLX_OUTPUT_PATH = args[3]
	parse_start = int(args[4])
	PROFILE_DATA_PATH = args[5]
	ROCKET_KEY = "75407k6c61c5895ff895ac57a9f733778130a3"
	VERIFY_KEY = "b3YYZnnVncA0iY9JgfwrI64q0V4kTPXGmOT466R5aLSFGtzQEp"
	print(LIST_LINK)
	retrieve_profiles = (LIST_LINK != "None")

	start_time = time.time()
	
	#driver = login(CONFIG_PATH)
	#profile_urls = get_profile_urls(driver, LIST_LINK, PROFILE_PATH)
	profiles_data = None
	if parse_start >= 0:
		with open(PROFILE_DATA_PATH) as datafile:
			profiles_data = json.loads(datafile.read())
	profile_urls = read_profile_urls(PROFILE_PATH)
	print(len(profile_urls), len(profiles_data))
	#profiles_data = parse_profiles(driver, profile_urls, XLX_OUTPUT_PATH, parse_start, profiles_data, PROFILE_DATA_PATH)
	profiles_data = verify_emails(profiles_data, ROCKET_KEY, VERIFY_KEY, PROFILE_DATA_PATH, parse_start)
	load_excel(profiles_data, XLX_OUTPUT_PATH)
	

	# else:
	# 	print("NO URL RETRIEVAL!")
	# 	profile_urls = read_profile_urls(PROFILE_PATH)

	# profiles_data = None
	# if parse_start != -1:
	# 	profiles_data = None
	# 	if parse_start > 0:
	# 		with open(PROFILE_DATA_PATH) as datafile:
	# 			profiles_data = json.loads(datafile.read())
	# 	if driver == None:
	# 		driver = login(CONFIG_PATH)
	# 	profiles_data = parse_profiles(driver, profile_urls, XLX_OUTPUT_PATH, parse_start, profiles_data, PROFILE_DATA_PATH)
	# else:
	# 	print("NO PARSES!")
	# 	print(PROFILE_DATA_PATH)
	# 	with open(PROFILE_DATA_PATH) as datafile:
	# 		profiles_data = json.loads(datafile.read())

	# if driver:
	# 	driver.close()

	# profiles_data_email = verify_emails(profiles_data, ROCKET_KEY, VERIFY_KEY, PROFILE_DATA_PATH)

	# load_excel(profiles_data_email, XLX_OUTPUT_PATH)

	execution_time = (time.time() - start_time)
	print('Execution time in seconds: ' + str(execution_time))

def read_config(CONFIG_PATH):
	lines = open(CONFIG_PATH).readlines()
	user, pw = lines[0], lines[1]
	return user, pw

def read_profile_urls(PROFILE_PATH):
	file = open(PROFILE_PATH)
	lines = file.readlines()
	profile_urls = []
	for line in lines:
		profile_urls.append(line)
	return profile_urls


def login(CONFIG_PATH):
	user, pw = read_config(CONFIG_PATH)

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--start-maximized")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
	chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
	chrome_options.add_experimental_option('useAutomationExtension', False)
	driver = webdriver.Chrome(options=chrome_options,executable_path="./chromedriver_98")
	driver.get("https://www.linkedin.com/sales/login")
	time.sleep(1)
	WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,".authentication-iframe")))
	driver.find_element_by_css_selector('#username').send_keys(user)
	driver.find_element_by_css_selector('#password').send_keys(pw)
	button = driver.find_element_by_css_selector('.login__form_action_container>button')

	print("found:", button)
	button.click()
	print("LOGGED IN")
	time.sleep(10)
	return driver

def get_profile_urls(mainDriver, LIST_LINK, PROFILE_PATH):
	mainDriver.get(LIST_LINK);
	idx = 2
	profile_urls = []
	buttons = []
	while idx <= 100:
		mainDriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		y = 1000
		for timer in range(0,7):
			mainDriver.execute_script("window.scrollTo(0, "+str(y)+")")
			y += 1000  
			time.sleep(1)

		divs = mainDriver.find_elements_by_class_name('result-lockup__name')

		for div in divs:
			url = div.find_element_by_css_selector('a').get_attribute('href')
			profile_urls.append(url)

		print(idx)
		button = None
		try:
			button = mainDriver.find_element_by_xpath('//button[@data-page-number="{}"]'.format(idx))
		except:
			print("Button not found!")
			break
		button.click()
		time.sleep(3)
		print(profile_urls[-1])
		print("# Profiles", len(profile_urls))
		idx += 1
	
	with open(PROFILE_PATH, 'w') as f:
		for url in profile_urls:
			f.write(url + "\n")


	print("Total # Profiles to Scrape", len(profile_urls))

	return "Finished"

def parse_profiles(driver, profile_urls, XLX_OUTPUT_PATH, parse_start, profile_data, PROFILE_DATA_PATH):
	profiles_data = {}
	if profile_data != None:
		profiles_data = profile_data
	else:
		profiles_data["Name"] = []
		profiles_data["# Years in Current Role"] = []
		profiles_data["Linkedin URL"] = []
		profiles_data["Email"] = []
		profiles_data["Email Verified? Yes/No"] = []
		profiles_data["Undergraduate College / University"] = []
		profiles_data["Location (city) of individual"] = []
		profiles_data["Location (state) of individual"] = []
		profiles_data["Current Company"] = []
		profiles_data["Current Company URL"] = []
		profiles_data["# LinkedIn Employees at Current Company"] = []
		profiles_data["Company industry category"] = []
		profiles_data["Location (city) of Company"] = []
		profiles_data["Location (state) of Company"] = []
	

	for idx, prof_url in enumerate(profile_urls):
		print("INDEX", idx)
		if idx < parse_start:
			continue
		if idx >= (parse_start + 600):
			break

		print("PROFILE {}".format(idx))
		driver.get(prof_url)
		time.sleep(1)
		name_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard-person-entity__name t-24 t-black t-bold"]')
		name = name_div.text
		print("Name", name)

		time.sleep(1)
		title_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard__summary-position-title"]')
		title = title_div.text
		print("Title", title)

		time_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard__time-period-bullet"]')
		time.sleep(1.5)
		num_years = time_div.text
		print("# Years", num_years)

		location_div = driver.find_element_by_xpath('.//div[@class = "profile-topcard__location-data inline t-14 t-black--light mr5"]')
		prof_loc = location_div.text
		prof_city, prof_state = "", ""
		if "," in prof_loc:
			text = prof_loc.split(",")
			prof_city = text[0]
			prof_state = text[1]

		print("Profile Location", prof_city + "," + prof_state)

		#Get Education Info
		time.sleep(1)
		edu_div = driver.find_elements_by_xpath('.//li[@class = "profile-education display-flex align-items-flex-start"]')
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
			company_div = driver.find_element_by_xpath('.//a[@class = "li-i18n-linkto inverse-link-on-a-light-background t-14 t-black t-bold"]')
			company_link = company_div.get_attribute('href')
			company_text = company_div.text
		except:
			company_div = driver.find_element_by_xpath('.//span[@class = "t-14 t-black t-bold"]')
			company_text = company_div.text

		industry, num_employees, comp_city, comp_state = "","","",""
		if company_link != "":
			driver.get(company_link)
			time.sleep(2)
			industry_div = None
			while industry_div is None:
				try:
					industry_div = driver.find_element_by_xpath('.//div[@class = "t-14"]')
					industry_raw = industry_div.text
					industry = industry_raw.split("·")[0]
				except:
					time.sleep(2)
					pass

			time.sleep(3.5)
			try:
				num_employees_div = driver.find_element_by_xpath('.//a[@class = "ember-view link-without-visited-and-hover-state"]')
			except:
				num_employees_div = None
				comp_loc = None

			if num_employees_div != None:
				is_thousand = "K" in num_employees_div.text
				num_employees = float(re.sub("[^\d.]+", "", num_employees_div.text))
				if is_thousand: num_employees *= 1000
				num_employees = int(num_employees)
				comp_loc_div = driver.find_element_by_xpath('.//div[@class = "t-12 t-black--light"]')
				comp_loc = comp_loc_div.text
				comp_city, comp_state = "", ""
				if "," in comp_loc:
					text = comp_loc.split(",")
					comp_city = text[0]
					comp_state = text[1]


		print("Company Info", company_link + " " + company_text + " "
			+ industry + " " + str(num_employees) + " " + comp_city + ", " + comp_state)

		profiles_data["Name"].append(name)
		profiles_data["# Years in Current Role"].append(num_years)
		profiles_data["Linkedin URL"].append(prof_url)
		profiles_data["Email"].append("")
		profiles_data["Email Verified? Yes/No"].append("No")
		profiles_data["Undergraduate College / University"].append(undergrad_text)
		if prof_city and prof_state:
			profiles_data["Location (city) of individual"].append(prof_city)
			profiles_data["Location (state) of individual"].append(prof_state)
		else:
			profiles_data["Location (city) of individual"].append(prof_loc)
			profiles_data["Location (state) of individual"].append(prof_loc)

		profiles_data["Current Company"].append(company_text)
		profiles_data["Current Company URL"].append(company_link)
		profiles_data["# LinkedIn Employees at Current Company"].append(num_employees)
		profiles_data["Company industry category"].append(industry)
		if comp_city and comp_state:
			profiles_data["Location (city) of Company"].append(comp_city)
			profiles_data["Location (state) of Company"].append(comp_state)
		else:
			profiles_data["Location (city) of Company"].append(comp_loc)
			profiles_data["Location (state) of Company"].append(comp_loc)
		

		## Save content to avoid running into viewing limit errors
		with open(PROFILE_DATA_PATH, 'w') as convert_file:
			convert_file.write(json.dumps(profiles_data))

	return profiles_data


def verify_emails(profiles_data, ROCKET_KEY, VERIFY_KEY, PROFILE_DATA_PATH, parse_start):
	names = profiles_data["Name"]
	companies = profiles_data["Current Company"]
	#Rocket Reach - Email Lookup
	rocket_url = "https://api.rocketreach.co/v2/api/lookupProfile"
	rocket_headers = {"Api-Key": ROCKET_KEY}
	#print(profiles_data['Email'].index('ricardo.king@promedica.org'))
	#return
	emails, verifies = profiles_data['Email'], profiles_data['Email Verified? Yes/No']
	#print(len(emails), len(verifies), len(names), len(companies) )
	print(len(emails), emails[-1], verifies[-1], names[-1])
	#print(parse_start)
	#return	
	#Check for padding sizes
	for idx, (name, company) in enumerate(zip(names, companies)):
		#Lookup Email
		if idx < parse_start:
			print(idx, parse_start, names[idx], emails[idx], verifies[idx])
			continue
		#else:
		#	print("START", idx, names[idx], emails[idx], verifies[idx])
		#	return
		rock_r = requests.get(rocket_url, data = {"name":name, "current_employer":company}, headers = rocket_headers)
		data = rock_r.json()
		email = ""
		if 'detail' not in data:
			email = data["current_work_email"]

		verified = "No"
		if email != "":
			verify_url = "https://app.verify-email.org/api/v1/{0}/verify/{1}".format(VERIFY_KEY, email)
			r = requests.get(verify_url)
			data = r.json()
			if data['status'] == 1:
				verified = "Yes"
		
		print(idx, name, company, email, verified)
		emails[idx] = email
		verifies[idx] = verified

		profiles_data["Email"] = emails
		profiles_data["Email Verified? Yes/No"] = verifies

		with open(PROFILE_DATA_PATH, 'w') as convert_file:
			convert_file.write(json.dumps(profiles_data))

	return profiles_data

def load_excel(profiles_data, XLX_OUTPUT_PATH):
	profiles_df = pd.DataFrame.from_dict(profiles_data)
	profiles_df.to_excel(XLX_OUTPUT_PATH, index = False)

if __name__ == "__main__":
	main()
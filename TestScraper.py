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

#Usage: python TestScraper.py config.txt "https://www.linkedin.com/sales/search/people?savedSearchId=50514333&searchSessionId=s6wrupLLSaGniUeEj6Rp%2Fw%3D%3D" output/profile_list.txt output/profiles.xlsx

def main():
	args = sys.argv[1:]
	print(len(args))
	CONFIG_PATH = args[0]
	LIST_LINK = args[1]
	PROFILE_PATH = args[2]
	XLX_OUTPUT_PATH = args[3]


	start_time = time.time()
	
	driver = login(CONFIG_PATH)
	#profile_urls = get_profile_urls(driver, LIST_LINK, PROFILE_PATH)
	profile_urls = read_profile_urls(PROFILE_PATH)
	parse_profiles(driver, profile_urls, XLX_OUTPUT_PATH)

	execution_time = (time.time() - start_time)
	print('Execution time in seconds: ' + str(execution_time))
	
	driver.close()


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
	driver = webdriver.Chrome(options=chrome_options,executable_path="./chromedriver")
	driver.get("https://www.linkedin.com/sales/login")
	time.sleep(1)
	#print(driver.get("https://www.linkedin.com"))
	print("REACHED 1")
	WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,".authentication-iframe")))
	print("REACHED 2")
	driver.find_element_by_css_selector('#username').send_keys(user)
	driver.find_element_by_css_selector('#password').send_keys(pw)
	print("LOGGED IN")
	time.sleep(10)
	return driver

def get_profile_urls(driver, list_link, OUTPUT_PROFILE_PATH):
	driver.get(list_link);
	#Iterate over pages
	idx = 2
	profile_urls = []
	buttons = []
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		y = 1000
		for timer in range(0,7):
			driver.execute_script("window.scrollTo(0, "+str(y)+")")
			y += 1000  
			time.sleep(1)

		divs = driver.find_elements_by_class_name('result-lockup__name')

		for div in divs:
			url = div.find_element_by_css_selector('a').get_attribute('href')
			profile_urls.append(url)

		print(idx)
		button = None

		try:
			button = driver.find_element_by_xpath('//button[@data-page-number="{}"]'.format(idx))
		except:
			break

		# if idx > 2:
		# 	break

		button.click()
		time.sleep(3)
		print("# Profiles", len(profile_urls))
		idx += 1
	
	print("Total # Profiles to Scrape", len(profile_urls))

	file = open(OUTPUT_PROFILE_PATH, 'w')
	for elem in profile_urls:
		file.write(elem + "\n")
	file.close()

	return profile_urls

def parse_profiles(driver, profile_urls, XLX_OUTPUT_PATH):
	profiles_data = {}
	profiles_data["First Name"] = []
	profiles_data["Last Name"] = []
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
		print("PROFILE {}".format(idx))
		driver.get(prof_url)
		name_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard-person-entity__name t-24 t-black t-bold"]')
		name_words = name_div.text
		name_words = name_words.split(" ")
		fname = re.sub("[^a-zA-Z]+", "", name_words[0])
		lname = re.sub("[^a-zA-Z]+", "", name_words[1])
		print("Name", fname + " " + lname)
		#profiles_data["First Name"].append(fname)
		#profiles_data["Last Name"].append(lname)
		time.sleep(1)
		title_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard__summary-position-title"]')
		title = title_div.text
		print("Title", title)

		time_div = driver.find_element_by_xpath('.//span[@class = "profile-topcard__time-period-bullet"]')
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
		time.sleep(1)
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
			time.sleep(1)
			industry_div = driver.find_element_by_xpath('.//div[@class = "t-14"]')
			industry_raw = industry_div.text
			industry = industry_raw.split("·")[0]

			time.sleep(1)
			num_employees_div = driver.find_element_by_xpath('.//a[@class = "ember-view link-without-visited-and-hover-state"]')
			is_thousand = "K" in num_employees_div.text
			#print("RAW EMPLOYEES", num_employees_div.text, str(is_thousand))
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



		profiles_data["First Name"].append(fname)
		profiles_data["Last Name"].append(lname)
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
		
		profiles_df = pd.DataFrame.from_dict(profiles_data)
		profiles_df.to_excel(XLX_OUTPUT_PATH, index = False)


if __name__ == "__main__":
    main()
# leadscraper
LinkedIn Sales Navigator - Lead List Scraper

Flask + Selenium, client-side version

## Installation
Run from root directory
```
python venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage
Run from root directory. 
```
python3 api/api.py
```

## Flow
1) Input Sales Nav credentials into login page. 
2) Input lead list url into page 2. Download the form data consisting of profile urls when done scraping. 
3) Input form data along with start index (LinkedIn only allows ~350 profile views a day). Output is a excel spreadsheet with profile + company data. There's inputs for rocket reach API key and verify-email API key that are prefilled, might want to change that or abstract away. 

## Note on EC2 Usage
If you do want to try web hosting on EC2, uncomment the following 2 lines in driver.py/login
```
##chrome_options.add_argument('--headless')
##driver = webdriver.Chrome(options=chrome_options,executable_path="/usr/bin/chromedriver")
```
and comment the following line
```
driver = webdriver.Chrome(options=chrome_options,executable_path="./chromedriver")
```

-----------------------------------DEPRECATED-------------------------------------------------------------
## Usage
```
python TestScraper.py CONFIG_PATH LEAD_LIST_LINK PROFILE_LIST_PATH EXCEL_PATH PARSE_START OUTPUT_PROFILE_DATA_PATH ROCKET_API_KEY VERIFY_API_KEY
```
CONFIG_PATH = Where the configuration file is stored. This should be a text file with the first line containing username and second line containing password (ex: config.txt)

LEAD_LIST_LINK = Link to lead list within sales navigator. Make sure it is in double quotes (ex: "www.linkedin.com/xxx"). Set to "None" if you already have crawled the lead list/have a profile_list.txt file. 

PROFILE_LIST_PATH  = Where the text file with profile urls is stored. This should be an empty text file (ex: output/profile_list.txt, where you have made a folder within the script's folder titled output)

EXCEL_PATH = Where the excel file is stored where information will be posted to (ex: output/profiles.xlsx)

PARSE_START = Where you want to start parsing the profile text file from. When parsing a large list (> 250 profiles) you will need to use this parameter and set it to the index of the profile you want to continue reading from (i.e. line 500 -> 499, python is 0-indexed). Regardless, the script will only allow you to parse 250 profiles in a single run(more on this in the notes section). Set this to -1 if you have already scraped profile-level information/have a profile_data.txt file. 

OUTPUT_PROFILE_DATA_PATH = Where to dump profile data as it is scraped (this should be a text file). This is to ensure that no information is lost if the script crashes due to bot detection. 

ROCKET_API_KEY/VERIFY_API_KEY = API keys for Rocket Reach and Verify-Email

### Sample Usage
1. End-To-End
```
python TestScraper.py config.txt "https://www.linkedin.com/sales/search/REDACTED" output/profile_list.txt output/profiles.xlsx 0 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY
```

2. Profile Parsing & Email Lookup/Verification
```
python TestScraper.py config.txt "None" output/profile_list.txt output/profiles.xlsx 10 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY
```


3. Email Lookup/Verification
```
python TestScraper.py config.txt "None" output/profile_list.txt output/profiles.xlsx -1 output/profiles_data.txt ROCKET_API_KEY VERIFY_API_KEY
```

## To Note
1. The script will automatically stop running after 250 profiles are viewed. This is to work around Sales Navigator's viewing limits (if exceeded, can lead to an account ban, important to not sidestep). Continue running the script from where you left off using the text file containing profile urls. 

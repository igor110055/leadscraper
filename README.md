# leadscraper
LinkedIn Sales Navigator - Lead List Scraper

## Installation
```
python venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage
```
python TestScraper.py CONFIG_PATH LEAD_LIST_LINK PROFILE_LIST_PATH EXCEL_PATH PARSE_START
```
CONFIG_PATH = Where the configuration file is stored. This should be a text file with the first line containing username and second line containing password (ex: config.txt)

LEAD_LIST_LINK = Link to lead list within sales navigator. Make sure it is in double quotes. (ex: "www.linkedin.com/xxx")

PROFILE_LIST_PATH  = Where the text file where profile urls is stored. This should be an empty text file (ex: output/profile_list.txt, where you have made a folder within the script's folder titled output)

EXCEL_PATH = Where the excel file is stored where information will be posted to (ex: output/profiles.xlsx)

PARSE_START (Optional, default is 0) = Where you want to start parsing the profile text file from. When parsing a large list (> 500 profiles) you will need to use this parameter and set it to the index of the profile you want to continue reading from (i.e. line 500 -> 499, python is 0-indexed). Regardless, the script will only allow you to parse 500 profiles (more on this in the notes section).

### Sample Usage

```
python TestScraper.py config.txt "https://www.linkedin.com/sales/search/people?savedSearchId=REDACTED" output/profile_list.txt output/profiles.xlsx
```

## To Note
1. The script will automatically stop running after 500 profiles are viewed. This is to work around Sales Navigator's viewing limits (if exceeded, can lead to an account ban, important to not sidestep). Continue running the script from where you left off using the text file containing profile urls. 

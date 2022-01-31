import requests 

name = "Raghav Anand"
company = "Skio"
ROCKET_KEY = "75407k6c61c5895ff895ac57a9f733778130a3"

rocket_url = "https://api.rocketreach.co/v2/api/lookupProfile"
rocket_headers = {"Api-Key": ROCKET_KEY}

rock_r = requests.get(rocket_url, data = {"name":name, "current_employer":company}, headers = rocket_headers)
data = rock_r.json()

print(data)
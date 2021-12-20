# leadscraper
LinkedIn Sales Navigator - Lead List Scraper

## Scrapy Shell Commands
grab class xpath: 
response.xpath('*[contains(@class, "ember-application boot-complete")]')
//*[contains(@class, "ember-application boot-complete")]

response.xpath('//*[@class = "ember-application boot-complete"]')

table = response.xpath('//*[@class = "names"]//tbody')

response.css('.ember-application boot-complete')
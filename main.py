from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.chrome.options import Options

import logging
import time
import json

def getExternalResourcesLoaded(driver):
    externalResources = set()
    chromelog = driver.get_log('performance')
    for request in chromelog:
        parsedMessage = json.loads(request["message"])["message"]
        if (parsedMessage["method"] == "Network.requestWillBeSent"):
            url = parsedMessage["params"]["request"]["url"]
            if(baseURL not in url):
                externalResources.add(url)
    return externalResources
 


def getLinkSet(driver):
    links = set()
    hrefs = driver.find_elements(By.XPATH, "//a[@href]")
    for href in hrefs:
        link = href.get_attribute("href").split("#")[0]
        if(baseURL in link):
            links.add(link)
    return links


# logger = logging.getLogger('selenium')
# logger.setLevel(logging.DEBUG)
baseURL = "https://cloudvil.com"

chrome_options = Options()
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-default-apps')
chrome_options.add_argument('--window-size=1920,1080')
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
cloud_options = {}
cloud_options['browser'] = "ALL"
cloud_options['performance'] = "INFO"
chrome_options.set_capability('goog:loggingPrefs', cloud_options)

driver = webdriver.Chrome(options=chrome_options)

links = set()
linksVisited = set()
links.add(baseURL)
while(len(links) > 0):
    link = links.pop()
    linksVisited.add(link)
    driver.get(link)
    time.sleep(1)
    print("PAGE TITLE: " + driver.title)
    externalResources = getExternalResourcesLoaded(driver)
    internalLinks = getLinkSet(driver)
    links.update(internalLinks)
    links.difference_update(linksVisited)
    print(links)
    print("Found " + str(len(externalResources)) + " externally loaded scripts")
    print("Found " + str(len(links)) + " internal links")




from socket import CAN_RAW
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.chrome.options import Options
import json
import logging
import time

class Webcrawler:
    def __init__(self, url, maxCrawlDepth=1):

        chrome_options = Options()
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        cloud_options = {}
        cloud_options['browser'] = "ALL"
        cloud_options['performance'] = "INFO"
        chrome_options.set_capability('goog:loggingPrefs', cloud_options)

        self.url = url
        self.maxCrawlDepth = maxCrawlDepth
        self.driver = webdriver.Chrome(options=chrome_options)
        self.linksToVisit = set()
        self.linksVisited = set()
        self.externalResources= {}

    def scanPageForExternalResources(self):
        chromelog = self.driver.get_log('performance')
        externalResources = set()
        for request in chromelog:
            parsedMessage = json.loads(request["message"])["message"]
            if (parsedMessage["method"] == "Network.requestWillBeSent"):
                url = parsedMessage["params"]["request"]["url"]
                if((self.url not in url) and (url.startswith("data:image") == False)):
                    externalResources.add(url)

        self.externalResources[self.driver.current_url] = externalResources
    
    def addInternalLinksToVisit(self, crawlDepth):
        hrefs = self.driver.find_elements(By.XPATH, "//a[@href]")
        for href in hrefs:
            link = href.get_attribute("href").split("#")[0]
            if(self.url in link and link not in self.linksVisited):
                self.linksToVisit.add((link, crawlDepth + 1))

    def close(self):
        self.driver.quit()

    def __del__(self):
        self.close()

    def printExternalResources(self):
        for url in self.externalResources:
            if(len(self.externalResources[url]) > 0):
                print(url)
                for externalResource in self.externalResources[url]:
                    print("\t" + externalResource)
    
    def crawl(self): 
        crawlDepth = 0   
        self.linksToVisit.add((self.url,crawlDepth))
        while(len(self.linksToVisit) > 0 and crawlDepth < self.maxCrawlDepth):
            link,crawlDepth = self.linksToVisit.pop()
            self.linksVisited.add(link)
            self.driver.get(link)
            self.scanPageForExternalResources()
            self.addInternalLinksToVisit(crawlDepth)

            print("Crawling depth " + str(crawlDepth) + "/" + str(self.maxCrawlDepth))
        print("Finished crawling " + self.url)
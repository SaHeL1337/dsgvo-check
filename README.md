# DSGVO Check written in python with selenium 4
## Technology
- Python
- Selenium 4
- FastAPI

## Features
- Scrapes a website, crawls through all internal links until it has found all the child pages
- Checks browser logs for external resources that are being loaded before consent is being give, indicating a dsgvo breach
- Javascript enabled

## Roadmap
- more checks for each website, like performance indicator, SEO, possible improvements
- dead link finder
- map of website to show heavily linked sites and less linked ones
- webfrontend so that you can run and see results in a nice ui
- backend service for saving the results in some database

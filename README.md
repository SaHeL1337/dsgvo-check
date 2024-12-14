# DSGVO Check written in python with selenium 4

## Current state
Work in progress/proof of concept and only for local use

## Features/Description
- Scrapes a website, crawls through all internal links until it has found all the child pages
- Checks browser logs for external resources that are being loaded before consent is being give, indicating a dsgvo breach
- Javascript enabled

## Technology
- Python3
- Selenium 4
- FastAPI
- Solace
- Flask
- Xlaunch
- SQLAlchemy/SQLite


## Roadmap
- more checks for each website, like performance indicator, SEO, possible improvements
- dead link finder
- map of website to show heavily linked sites and less linked ones
- webfrontend so that you can run and see results in a nice ui
- backend service for saving the results in some database
- reduce unnecessary prints/outputs


## Setup
go to /config.ini and change the connection settings for your solace broker

## Start solace broker
Assuming a compatible solace broker is running (out of scope for this project)
Running it locally works for development:
Open Docker Desktop
Start Solace broker container

## Start Backend
source env/bin/activate
python3 backend.py
start xlaunch program for selenium driver to work

## Start Frontend (not for production use)
source env/bin/activate
flask --debug run


## Usage
go to https://localhost:5000
Type URL into search bar
crawling starts

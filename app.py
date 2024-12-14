import email
from flask import Flask, render_template, redirect
from Webcrawler import Webcrawler
from flask import request
from urllib.parse import urlparse
from SolaceBroker import SolaceBroker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db_session
from Models.Result import Result
from database import init_db
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
SOLACE_HOST = config['SOLACE']['HOST']
SOLACE_VPN = config['SOLACE']['VPN']
SOLACE_USERNAME = config['SOLACE']['USERNAME']
SOLACE_PASSWORD = config['SOLACE']['PASSWORD']

app = Flask(__name__)
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['EXECUTOR_MAX_WORKERS'] = 2

urlQueue = []

if __name__ == '__main__':
    app.run(debug=True)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@app.route('/', methods=['GET'])
def home():
    baseUrl = request.args.get('url')
    init_db()
    results = Result.query.filter_by(baseUrl=baseUrl).all()
    resultsFound =len(results)
    pagesCrawled = len(set([result.crawledUrl for result in results]))
    return render_template("index.html", baseUrl=baseUrl, results=results, resultsFound=resultsFound, pagesCrawled=pagesCrawled)

@app.route('/crawl', methods=['POST'])
def addUrlToQueue():
    baseUrl = request.form.get('url')
    results = Result.query.filter_by(baseUrl=baseUrl).all()
    for result in results:
        db_session.delete(result)
        db_session.commit()

    if not is_valid_url(baseUrl):
        return 'Invalid URL', 400
 
    broker = SolaceBroker(SOLACE_HOST,SOLACE_VPN,SOLACE_USERNAME,SOLACE_PASSWORD)
    broker.publish(baseUrl, "t/crawl")

    return redirect("/?url=" + baseUrl, code=302)

@app.route('/delete', methods=['GET'])
def delete():
    baseUrl = request.args.get('url')
    results = Result.query.filter_by(baseUrl=baseUrl).all()
    for result in results:
        db_session.delete(result)
        db_session.commit()
    
    return redirect("/?url=" + baseUrl, code=302)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
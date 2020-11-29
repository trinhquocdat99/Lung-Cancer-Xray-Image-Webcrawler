from flask import Flask, request
from flask_cors import CORS, cross_origin

from scrapper import Scrapper, urlExists, isDataUrl
from customScrapper import CustomScrapper, isInCustomSites
from xrayClassification import isImageXray
import requests
from io import BytesIO
from urllib.request import urlopen

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/scrape', methods=['POST'])
@cross_origin(supports_credentials=True)
def scrapeURL():
    data = request.json
    url = data['url']
    response = dict()
    scrapper = None

    if urlExists(url, timeout=20, check_is_image=False):
        if isInCustomSites(url):
            scrapper = CustomScrapper()
            response['custom'] = True
        else:
            scrapper = Scrapper()
            response['custom'] = False

        image_or_data_urls = scrapper.scrape(url)
        if len(image_or_data_urls) > 0:
            response['success'] = True
            response['output'] = image_or_data_urls
            response['stats'] = scrapper.stats
        else:
            response['success'] = False
            response['output'] = "NO_IMAGES_FOUND"
    else:
        response['success'] = False
        response['output'] = "INVALID_URL"

    return response


@app.route('/xray_image_classification_model', methods=['POST'])
@cross_origin(supports_credentials=True)
def classifyImage():
    data = request.json
    url = data['url']
    response = dict()
    try:
        if isDataUrl(url):
            response_ = urlopen(url).read()
            img = BytesIO(response_)

        else:
            response_ = requests.get(url, timeout=5)
            img = BytesIO(response_.content)

        response['prediction'] = isImageXray(img, return_bool=False)
        response['success'] = True
    except:
        response['success'] = False

    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80, threaded=False)

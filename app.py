from flask import Flask, request
from flask_cors import CORS, cross_origin

from scrapper import scrape, urlExists

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
    if urlExists(url):
        image_urls = scrape(url)
        if len(image_urls) > 0:
            response['success'] = True
            response['output'] = image_urls
        else:
            response['success'] = False
            response['output'] = "NO_IMAGES_FOUND"
    else:
        response['success'] = False
        response['output'] = "INVALID_URL"

    return  response



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80, threaded=False)

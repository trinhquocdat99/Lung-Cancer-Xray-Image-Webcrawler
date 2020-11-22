from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
def hello_world():
    return 'Hello World!'




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80, threaded=False)

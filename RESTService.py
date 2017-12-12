from flask import Flask
from athletes import API

app = Flask(__name__)

@app.route('/')
def index():
    return API.findAthleteResults("Erika Sampaio").to_html()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
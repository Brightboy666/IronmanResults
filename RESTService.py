from flask import Flask
from athletes import API

app = Flask(__name__)

@app.route('/')
def index():
    return API.findAthleteResults("").to_csv()

if __name__ == '__main__':
    app.run(debug=True)
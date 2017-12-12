from flask import Flask
from athletes import API

app = Flask(__name__)

@app.route('/fast/<format>')
def fast(format="html"):
    if format=="html":
        return API.findFastResults().to_html()
    else:
        return API.findFastResults().to_csv()

@app.route('/fastest/<format>')
def fastest(format="html"):
    if format=="html":
        return API.findFastestResults().to_html()
    else:
        return API.findFastestResults().to_csv()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
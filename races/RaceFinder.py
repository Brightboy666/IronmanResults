#!flask/bin/python
from flask import Flask, jsonify
from flask import abort, make_response, request

app = Flask(__name__)

races = [
    {
        'id': 1,
        'title': u'race name',
        'year': u'2016', 
        'url': False
    }
]




@app.route('/v1.0/races', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': races})


if __name__ == '__main__':
    app.run(debug=True)
    

#http://www.coachcox.co.uk/ironman-statistics-by-race/ironman-results-statistics-links/
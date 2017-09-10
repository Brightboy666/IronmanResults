from pymongo import MongoClient

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import datetime

headers = {'User-Agent':'Mozilla/5.0'}
results_folder = "results"

class ResultsCache:    
    
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.html    
        self.collection = self.db.html

    def getHTML(self, url):
        req = Request(url, None, headers)
        html = urlopen(req).read()

        # results = self.collection.find({"_id":url})
        
        # if(results.count() == 1):
        #     return str(results[0]['html'])
        # elif(results.count() > 1):
        #     raise Exception('Multiple results for '+ url + ' in table')
        
        # self.collection.insert({
        #     '_id' : url,
        #     'html':html,
        #     "timestamp": datetime.datetime.now()}
        # )
        
        return html
    
    def removeCachedItems(self, url):
        self.collection.remove({"_id":url})
    
    def getNumberOfCachedItems(self):
        return self.collection.count()
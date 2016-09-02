
import urllib, csv
from bs4 import BeautifulSoup
import pickle

headers = {'User-Agent':'Mozilla/5.0'}
results_folder = "csv_results"

def getTitle(soup):
    try:
        return soup.find('meta')['content']
    except:
        return ""
    
def getSpreadsheetUrls(urls):
    spreadsheet_urls = []
    
    
    return spreadsheet_urls

def getResultsPages():
    # parts of paginated urls
    urls = []
    # get the data out of each row, append to records list
    morePages = True
        
    try:
        
        while (morePages):
            homepage_url = 'http://www.ironman.com/triathlon/coverage/past.aspx#axzz4J3QWfTDf'
            html = urllib.request.urlopen(urllib.request(homepage_url, None, headers)).read()
            soup = BeautifulSoup(html, "lxml") # a list to hold our urls
            links = soup.findAll('a', href=True, text='Event Details')
            for link in links[1:]:
                try:
                    url.append(link['href'])
                except:
                    pass
            link = soup.find('a', href=True, title="Next")
            
            homepage_url = link['href']
    
    except Exception as e:
        print(e)
        
    return urls

urls = getResultsPages()    
#spreadsheet_urls = getSpreadsheetUrls(urls)
 
    
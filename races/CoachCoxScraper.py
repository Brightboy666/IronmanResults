
import urllib2, csv
from bs4 import BeautifulSoup
import pickle

headers = {'User-Agent':'Mozilla/5.0'}
spreadsheet_file = 'spreadsheet_urls.txt'
results_folder = "csv_results"

def getTitle(soup):
    try:
        return soup.find('meta')['content']
    except:
        return ""
    
def getSpreadsheetUrls(urls):
    spreadsheet_urls = []
    
    with open(spreadsheet_file, 'wb') as f:        
        for url in urls:
            print url
            html = urllib2.urlopen(urllib2.Request(url, None, headers)).read()
            soup = BeautifulSoup(html, "lxml") # a list to hold our urls
            links = soup.findAll('a')
    # get the data out of each row, append to records list
            for link in links[1:]:
                try:
                    href = link['href']
                    if "docs.google" in href:
                        if href not in spreadsheet_urls:
                            spreadsheet_urls.append(href)
                except:
                    pass
        
        pickle.dump(spreadsheet_urls, f)
    
    return spreadsheet_urls

def getResultsPages():
    # parts of paginated urls
    homepage_url = 'http://www.coachcox.co.uk/ironman-statistics-by-race/ironman-results-statistics-links/'
    html = urllib2.urlopen(urllib2.Request(homepage_url, None, headers)).read()
    soup = BeautifulSoup(html, "lxml") # a list to hold our urls
    urls = []
    links = soup.findAll('a')
# get the data out of each row, append to records list
    for link in links[1:]:
        try:
            href = link['href']
            if "-results-" in href:
                if href not in urls:
                    urls.append(href)
        except:
            pass
    
    return urls

#urls = getResultsPages()    
#spreadsheet_urls = getSpreadsheetUrls(urls)
 
spreadsheet_urls = []
with open(spreadsheet_file, 'rb') as f:
   spreadsheet_urls = pickle.load(f)
        
print(spreadsheet_urls)

for url in spreadsheet_urls:
    try:
        html = urllib2.urlopen(urllib2.Request(url, None, headers)).read()
        soup = BeautifulSoup(html, "lxml") # a list to hold our urls
        
        title = getTitle(soup)
        key = ""
        
        if "ccc?key" in url:
            key = url.split('/')[4].split('ccc?key=')[1].split('&')[0]
        else:
            key = url.split('/')[5]
            
        csv_url = "https://docs.google.com/feeds/download/spreadsheets/Export?key={}&exportFormat=csv".format(key)
        print csv_url
        
        if title is "":
            title = key
        
        file("{}/{}.csv".format(results_folder, title), "w").write(urllib2.urlopen(csv_url).read())
    except Exception, e:
        print "Error with {}. Error {}".format(url,e)
    
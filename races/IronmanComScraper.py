
import csv
from bs4 import BeautifulSoup
import pickle
import re

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

headers = {'User-Agent':'Mozilla/5.0'}
results_folder = "results"

def getTitle(soup):
    try:
        return soup.find('meta')['content']
    except:
        return ""
    

def getsoup(url):
    req = Request(url, None, headers)
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "lxml") # a list to hold our urls
    return soup

def outputRaceResults(url):
    soup = getsoup(url)
    
    race = url.split('/')[6] +'-'+ url.split('/')[7]+'-'+ url.split('/')[8].split('=')[1]+".csv"
    
    with open(results_folder +"/"+ race, "wt") as f:
        writer = csv.writer(f) 
        writer.writerow(["#"+race])
              
        for i in range(174,3000):
            
            try:
                len(soup.find('iframe', {"id":"trackerFrame"}))> 0
                break
            except:
                athlete = url +"&bidid={}&detail=1".format(i)
                soup = getsoup(athlete)
                
                name = ""
                
                for h in soup.findAll('h1'):
                    if h.parent.name == 'header' and h.contents[0].strip() != "":
                        name = h.contents[0].strip()
                        break


                bib = ""
                age = ""
                state = ""
                country = ""


                genInfo = soup.find('table', id="general-info").find('tbody')
                for tr in genInfo.findAll('tr'):
                    value = tr.findAll('td')[0].contents[0].contents[0]                                        
                    print(value)
                    
                    if "BIB" in value:
                        bib = tr.findAll('td')[1].contents[0]
                    elif "Age" in value:
                        age = tr.findAll('td')[1].contents[0]
                    elif "State" in value:
                        state = tr.findAll('td')[1].contents[0]
                    elif "Country" in value:
                        country = tr.findAll('td')[1].contents[0]

                swimTime=""
                bikeTime=""
                runTime=""
                overallTime=""

                splitsTable = soup.find('table', id="athelete-details").find('tbody')
                for tr in splitsTable.findAll('tr'):
                    value = tr.findAll('td')[0].contents[0].contents[0]                                        
                    print(value)
                    
                    if "Swim" in value:
                        swimTime = tr.findAll('td')[1].contents[0]
                    elif "Bike" in value:
                        bikeTime = tr.findAll('td')[1].contents[0]
                    elif "Run" in value:
                        runTime = tr.findAll('td')[1].contents[0]
                    elif "Overall" in value:
                        overallTime = tr.findAll('td')[1].contents[0]


                rank = soup.find('div', id="div-rank").contents[1] #overall rank. DIV ID is poorly named
                divRank = soup.find('div', id="rank").contents[1] #div rank. DIV ID is poorly named
                genderRank = soup.find('div', id="gen-rank").contents[1] #overall rank. DIV ID is poorly named
                
                #title = soup.find('p', text = re.compile(ur"Transition Details", re.DOTALL))
                print(name)
            
            
def getResultUrls(urls):   
    result_urls=[] 
    for url in urls:
        soup = getsoup(url)
        
        url = soup.find('div', {"class": "navWrapper"}).find('a', href=True, text='Results')['href']        
        soup = getsoup(url)        
        
        #div = soup.findAll("ul"
        links = soup.find('ul', { "id" : "raceResults" }).findAll('a', href=True)
        
        for link in links:
            result_urls.append(link['href'])
        
    return result_urls

def getResultsPages():
    # parts of paginated urls
    urls = []
    # get the data out of each row, append to records list
    morePages = True
        
    try:
        homepage_url = 'http://www.ironman.com/triathlon/coverage/past.aspx#axzz4J3QWfTDf'
        
        while (morePages):    
            req = Request(homepage_url, None, headers)
            html = urlopen(req).read()
            soup = BeautifulSoup(html, "lxml") # a list to hold our urls
            links = soup.findAll('a', href=True, text='Event Details')
            for link in links[1:]:
                try:
                    urls.append(link['href'])
                except:
                    pass
                
            try:
                link = soup.find('a', href=True, title="Next")
                homepage_url = link['href']
                morePages = True
                return urls
            except:
                morePages = False
    
            print(homepage_url)
    except Exception as e:
        print(e)
        
    return urls


outputRaceResults("http://www.ironman.com/triathlon/events/americas/ironman-70.3/foz-do-iguacu/results.aspx?rd=20160827")

urls = getResultsPages()    
print(urls)

urls = getResultUrls(urls)
print(urls)
    
for url in urls:
    outputRaceResults(url)
    
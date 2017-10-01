
from bs4 import BeautifulSoup
import concurrent.futures
import csv
import logging
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import os.path
import pickle
import re
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from ResultsCache import ResultsCache

logger = logging.getLogger(__name__)
logging.basicConfig(filename='warnings_errors.log',level=logging.WARNING)  
results_folder = "races/results"

def getsoup(url):
    html =  ResultsCache().getHTML(url)
    
    if html is None:
        print("No html found for "+ url)
        return None
    else:
        soup = BeautifulSoup(html, "lxml") # a list to hold our urls
        return soup


def getAthleteName(soup):
    name = ""
    try:
        for h in soup.findAll('h1'):
            if h.parent.name == 'header':
                if h.contents[0].strip() != "":
                    if "View Full" not in h.contents[0].strip():
                        name = h.contents[0].strip()
                        break
    except:
        pass
    
    return name

def scrapeAthlete(soup, race):
    name = getAthleteName(soup)
    
    if name == "":
        return []
    
    bib = ""
    age = ""
    state = ""
    country = ""
    genInfoTable = soup.find('table', id="general-info")
    
    if genInfoTable is None:
        return []
    
    genInfo = genInfoTable.find('tbody')
    for tr in genInfo.findAll('tr'):
        value = tr.findAll('td')[0].contents[0].contents[0]
        if "BIB" in value:
            bib = tr.findAll('td')[1].contents[0]
        elif "Age" in value:
            age = tr.findAll('td')[1].contents[0]
        elif "State" in value:
            state = tr.findAll('td')[1].contents[0]
        elif "Country" in value:
            country = tr.findAll('td')[1].contents[0]
    
    swimTime = ""
    bikeTime = ""
    runTime = ""
    overallTime = ""
    
    splitsTable = soup.find('table', id="athelete-details").find('tbody')
    for tr in splitsTable.findAll('tr'):
        value = tr.findAll('td')[0].contents[0].contents[0]
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
    
    t1Time = soup.find(text=re.compile("T1")).parent.parent.findAll("td")[1].text
    t2Time = soup.find(text=re.compile("T2")).parent.parent.findAll("td")[1].text
    
    row = [race, bib, name, age, state, country, swimTime, bikeTime, runTime, t1Time, t2Time, overallTime]
    return row

#Gets the max bib for a race that we've already scraped and continues searching from that
#If it returns isEmptyRace=True it means we've already tried scraping it and ascertained there 
#are no results in it (for some reason Ironman has pages that exist for races that didn't.
def getMaxBib(fileLocation):
    maxBib = 1;
    isEmptyRace = False
    
    with open(fileLocation, "rt") as f:
        reader = csv.reader(f)
           
        for row in reader:
            if len(row) > 1:
                try:
                    maxBib = max(int(row[1]), maxBib) #Will keep going until the last bib available in the file
                except:
                    pass
            else:
               line = row[0]
               if "#EmptyRace" in line:
                   isEmptyRace = True 
            
    return maxBib, isEmptyRace

#Provides the links to individual race results for previous years
#Scrapes the file by going through every bib number
def outputRaceResults(url):
    try:
        soup = getsoup(url)
        


        #Race distance/race location/race date!, e.g.
        #ironman-70.3-zell-am-see-kaprun-20150829.csv
        split_url = url.split('/')

        if "inactive" in url:
            race = split_url[6] +'-'+ split_url[8]+'-'+ split_url[9].split('=')[1]+".csv"
        else:
            race = split_url[6] +'-'+ split_url[7]+'-'+ split_url[8].split('=')[1]+".csv"
        
        fileLocation = results_folder + "/" + race
        
        startBib = 1
        if os.path.exists(fileLocation):
            #THIS IS USED TO RESTART SCRAPING FOR A RACE WHERE WE ALREADY HAVE RESULTS
            #IT WILL FIND THE HIGHEST BIB NUMBER IN THE CSV AND RESTART FROM THERE.
            
            maxBibInFile, isEmptyRace = getMaxBib(fileLocation)
            
            if isEmptyRace:
                print("Empty Race found "+ fileLocation)
                return
            
            startBib = max(startBib, maxBibInFile+1)
            
        if startBib < 2:
            mode = "wt"
        else:
            mode = "at"
        
        with open(fileLocation, mode) as f:
            writer = csv.writer(f) 
            
            maxBib = 100 #We'll start looking through the first 100 in case the first few numbers aren't assigned.
            emptyRace = True   

            if startBib < 2: #Don't need to add headers as they'll be in there already
                writer.writerow(["#File="+race])      
                writer.writerow(['race', 'bib', 'name', 'age', 'state', 'country', 'swimTime', 'bikeTime', 'runTime', 't1Time', 't2time', 'overallTime'])
            else:
                emptyRace = False
                maxBib = startBib + 100 #If we're restarting we'll look through the next 100 numbers for more people
            
                         
            
            try:            
                #WILL KEEP SEARCHING FOR ATHLETES UNTIL IT FINDS 50 NUMBERS CONSECUTIVELY WHERE THERE
                #ARE NO RESULTS. NEED TO TEST IF THERE ARE ANY RACES WHERE THE BIBS START ABOVE 50, E.G. AN AMATEUR RACE WITH NO PROS?
                for i in range(startBib,3500):
                    if i > maxBib:
                        emptyRace = False
                        break
                    
                    try:
                        len(soup.find('iframe', {"id":"trackerFrame"}))> 0
                        logging.debug("Ignoring "+ url) #Research shows iframes for results are only used when the results are blank
                        break
                    except:
                        athlete = url +"&bidid={}&detail=1".format(i)
                                            
                        soup = getsoup(athlete)                
                        row = scrapeAthlete(soup, race)
                        
                        if len(row) > 0:
                            emptyRace = False
                            writer.writerow(row)
                            print(row)
                            maxBib = max(maxBib, i + 50)
            except Exception as e:
                logging.error("Error with "+url +". "+ str(e))
                emptyRace = False
                #We don't know if it is fact, empty, yet.
        
            if emptyRace:
                writer.writerow(['#EmptyRace'])
                writer.writerow(['#HighestBibChecked='+str(maxBib)])
    except Exception as e:
            logger.exception(e)#"Unknown Error with "+url +". ")
               
#Visits the home page for each race and then traverses the
#DOM to grab all links to previous results            
def getResultUrls(urls):   
    
    result_urls=[] 
    for url in urls:
        print("Processing {}".format(url))
        soup = getsoup(url)
        
        try:            
            resultsLink = soup.find('div', {"class":"navWrapper"}).find('a', href=True, text='Results')
            
            if resultsLink is None:
                logging.debug("No results found for "+ url)
                continue
            
            url = resultsLink['href'] 
                 
            soup = getsoup(url)        
        
            #div = soup.findAll("ul"
            raceResultsUL = soup.find('ul', {"id":"raceResults"})
            
            if raceResultsUL is None:
                logging.warning(url + ' has results in the non-standard format')
                continue
            
            links = raceResultsUL.findAll('a', href=True)
            
            for link in links:
                print("Found a race to scrape: {}".format(link['href']))
                result_urls.append(link['href'])
        except Exception as e:
            logging.exception("Error with "+url +". ")
    return set(result_urls)

def getResultsPages():
    # parts of paginated urls
    urls = []
    # get the data out of each row, append to records list
    morePages = True
        
    try:
        homepage_url = 'http://www.ironman.com/triathlon/coverage/past.aspx#axzz4J3QWfTDf'
        
        #FINDS ALL RACES LISTED
        #NEED TO FIGURE OUT A WAY TO MONITOR NEW RESULTS? I BELIEVE LIVE RACE RESULTS HAVE A DIFFERENT FORMAT.
        while (morePages):    
            soup = getsoup(homepage_url)
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
                #return urls
            except:
                morePages = False
    
            print(homepage_url)
    except Exception as e:
            logging.exception("Error with "+ homepage_url +". ")
        
    return set(urls)

import pickle

#TODO-If max bib = 100 then skip any scrapping for empty raaces

try: 
   result_page_urls = pickle.load( open( "result_page_urls.p", "rb" ) )
except:
    result_page_urls = getResultsPages()  
    pickle.dump(result_page_urls, open( "result_page_urls.p", "wb" ) )  
print(result_page_urls)

try: 
   urls = pickle.load( open( "urls.p", "rb" ) )
except:
    urls = getResultUrls(result_page_urls)
    pickle.dump(urls, open( "urls.p", "wb" ) )  
print(urls)
    
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for url in urls:
        pool.submit(outputRaceResults, url)    
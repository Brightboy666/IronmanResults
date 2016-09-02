import csv
import os


from fuzzywuzzy import fuzz


def getName(line):
    try:
        return line['Name']
    except: 
        try:
            return line['First Name'] +' '+ line['Last Name']
        except: 
            return "NA"
        
def getTime(line):
    try:
        return line['Overall']
    except: 
        try:
            return line['Overall Summary Time']
        except: 
            try:
                return line['Finish']
            except: 
                try:
                    return line['26.2 Mi Run Race Time']
                except: 
                    try:
                        return line['Run Total Race Time']
                    except: 
                        try:
                            return line['Overall Time']
                        except: 
                            return "Unknown"
                

def getDivision(line):
    try:
        return line['Division']
    except: 
        try:
            return line['Category']
        except: 
            return "Unknown"

def getRank(line):
    try:
        return int(line['Division Rank'])
    except: 
        try:
            return int(line['Finish Category Rank'])
        except: 
            try:
                return int(line['Rank'])
            except: 
                return 99999

lookFor = "M35-39"
matches = []

with open('../athletes/im hefei.csv', "rt" ) as theFile:
    reader = csv.DictReader( theFile )
    for line in reader:
        if line['ag'] == lookFor:
            matches.append(line)
            
            
for match in matches:
    #print(match['name'])
    pass

print ("Found " + str(len(matches)) + " matches")

results = []

resultsDir = '../races/csv_results'
files = os.listdir(resultsDir)


with open("im hefei.csv", "wt") as f:
    writer = csv.writer(f)
    writer.writerow(['Name'])

    for file in files:
        fileLoc = resultsDir +'/'+ file
        
        print("Opening "+ fileLoc)
        try: 
            with open(fileLoc, "rt" ) as theFile:
                    reader = csv.DictReader( theFile )
                    
                    for line in reader:
                        try:
                            rank = getRank(line)
                            div = getDivision(line)
                            time = getTime(line)
                            name = getName(line)
                            if div == "M25-29" and rank < 40:       
                                
                                for match in matches:
                                    ratio = fuzz.ratio(name.lower().rstrip(), match['name'].lower().rstrip())
                                    
                                    if ratio > 85:
                                        print("################ Match={},Name={},Time={}".format(match['name'], name, time))
                                        writer.writerow([match['name'], match['ag'], time])
                        except Exception as e:
                            print("Error with {}. Error {}".format(fileLoc,e))
        except Exception as ex:
            print("Error with {}. Error {}".format(fileLoc,ex))
                             
                        
                        
                        
                        
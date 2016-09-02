import csv
import pickle

from fuzzywuzzy import fuzz

def returnAG(sex, age):
    age = int(age) 
    lowerAge= int(age / 5) * 5
    upperAge = lowerAge + 4
    
    if age < 25 and age > 17:
        lowerAge = 18
        upperAge = 24
    
    if age < 18:
        return "Error"
    
    if  "MALE" in sex:
        sex = "M"
    elif "FEMALE" in sex:
        sex = "F"
    
    return "{}{}-{}".format(sex, lowerAge, upperAge).strip()

def outputAthlete(record):
    output = [
        (record[1].rstrip() + ' ' + record[0].rstrip()).strip().replace('\t', ''),
        returnAG(record[2], record[3]), 
        "" if len(record) == 4 else record[4].strip()
    ] #No home state
    
    #print "{}   {}".format(returnAG(record[2], record[3]),record[3])
    
    return output

if __name__ == '__main__':
    pass

file = open('hefei.txt', 'r')

with open("im hefei.csv", "wt") as f:
    writer = csv.writer(f)
    
    for line in file:
        tokens = line.split("  ")
        str = ""
        
        record = []
        
        for token in tokens:
            if token is "":
                continue
            record.append(token.rstrip().replace('\x0c', ''))
            
        if len(record) >3:   
            if "LAST NAME" in record[0]  :
                continue
            
            output= outputAthlete(record)    
            writer.writerow(output)
           # print output
        #print record
        

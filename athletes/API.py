from athletes.AthleteLoader import get_results
from athletes.Results import Division
import pandas as pd

def findAthleteResults(name:str, is_regex:bool = False):
    results = []

    for df in get_results():
        if is_regex:
            results.append(df[df['name'].str.match(name)])
        else:
            results.append(df[df['name'].str.contains(name)])

    return pd.concat(results)

def findFastResults():
    results = []

    for df in get_results():
        #We're removing athletes with slow times because we're not going to need to look at them
        #for predicting who is worth watching at an upcoming race.
        a = df.ix[((df['overallTime'] < pd.Timedelta('11:45:00')) & (df['overallTime'] > pd.Timedelta('07:20:00')) & (~df['raceName'].str.contains("70.3")))]
        b = df.ix[((df['overallTime'] < pd.Timedelta('5:45:00')) & (df['overallTime'] > pd.Timedelta('3:20:00')) & (df['raceName'].str.contains("70.3")))]
    
        results.append(a)
        results.append(b)
    return pd.concat(results)

def findFastestResults(breach:int = 15):
    results = []

    for df in get_results():
        #Finding the fastest athlete's per race. We'll need to figure out how to separate out pros and non-pros
        df = df.sort_values(by='overallTime', ascending=True).head(n=breach)
        results.append(df)

    return pd.concat(results)

def filter_by_ag(div:Division):
    results = []

    for df in get_results():
        #Finding the fastest athlete's per race. We'll need to figure out how to separate out pros and non-pros
        df = df[df['currentAge'].between(div.lowAge, div.highAge)]
        results.append(df)

    return pd.concat(results)

if __name__ == "__main__":
    #print(findAthleteResults("Erika.*Sampaio", is_regex=True))
    print(findFastestResults(breach=20))
    

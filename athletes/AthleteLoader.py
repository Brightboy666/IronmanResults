import csv
import os

from fuzzywuzzy import fuzz
from Results import Division

import logging

import re
import datetime

logger = logging.getLogger(__name__)

import pandas as pd

def get_results_for_ag(div:Division):
    resultsDir = 'races/results'
    files = (x for x in os.listdir(resultsDir) if str(x).endswith(".csv"))# and ("70.3-b" in str(x) or "70.3-m" in str(x)))

    master_df = None
    #div_list = []

    for file in files:

        if "5150" in file:
            #For now we are going to ignore Olympic distance events
            continue

        try:
            csv_location = "{}/{}".format(resultsDir, file)

            #First row will be a description of the file
            div_df = pd.DataFrame.from_csv(csv_location, header=1)

            if(len(div_df) < 10):
                logger.debug("{} likely to be an empty race".format(csv_location))
                continue

            enrich_dataframe(div_df, file)
            div_df = filter_by_ag(div_df, div)
            div_df = filter_to_fast(div_df)
            master_df = div_df if master_df is None else pd.concat([master_df, div_df])
        except Exception as e:
            logger.exception("Had an issue with: {}".format(file))
            logger.exception(e)

    return master_df


def enrich_dataframe(tmp_df, file):
    #Setting times for these peeps as beng very slow
    div_df.ix[div_df.overallTime.isin(['DNS', 'DNF', 'DQ', '---', pd.np.nan]), 'overallTime'] = "19:59:59"
    div_df['overallTime'] = pd.to_timedelta(div_df['overallTime'])

    #Changing values that aren't valid ages to 0 so they don't match
    #the following filter
    try:
        tmp_df[['age']]

        tmp_df.ix[tmp_df.age.isin(['---', pd.np.nan]), 'age'] = 0
        tmp_df['age'].astype(int)
    except Exception as e:
        print("")

    tmp_df.ix[tmp_df.age.isin(['---', pd.np.nan]), 'age'] = 0
    tmp_df['age'] = tmp_df['age'].astype(int)

    #We'll figure out the current age of each competitor.
    #For example if someone was 24 when they raced two years ago
    #They will now be 26 and we'll need this to know they are now
    #in the 25-29 category, for example.
    yrOfRace = int(re.match(".*-(\d\d\d\d)", file, re.IGNORECASE).group(1))
    currentYr = datetime.datetime.today().year
    yrsSinceRace = currentYr - yrOfRace
    tmp_df['currentAge'] = tmp_df['age'] + yrsSinceRace

    #Grabbing the date of the race from the file name in case we need it.
    dateMatch = re.match(".*-(\d\d\d\d)(\d\d)(\d\d)", file, re.IGNORECASE)
    raceDate = datetime.datetime(year=int(dateMatch.group(1)), month=int(dateMatch.group(2)), day=int(dateMatch.group(3)))
    tmp_df['raceDate'] = raceDate

    #Grabbing the race name from the file name
    #We may want to change the structure of the files to have columns for
    #race name, date and distance, although that would be a lot of 
    #repeating data to go in the files...
    raceMatch = re.match(".*?-(70\.3)?[-]?(.*)-.*", file, re.IGNORECASE)
    raceName = "{}-{}".format(raceMatch.group(1), raceMatch.group(2)) if raceMatch.group(1) is not None else "{}".format(raceMatch.group(2))
    tmp_df['raceName'] = raceName

    #Getting rid of the index which is the file name (we don't need it anyway)
    tmp_df.reset_index(drop=True, inplace=True)


def filter_to_fast(df:pd.DataFrame):
    #We're removing athletes with slow times because we're not going to need to look at them
    #for predicting who is worth watching at an upcoming race.
    a = df.ix[((df['overallTime'] < pd.Timedelta('11:45:00')) & (df['overallTime'] > pd.Timedelta('07:20:00')) & (~df['raceName'].str.contains("70.3")))]
    b = df.ix[((df['overallTime'] < pd.Timedelta('5:45:00')) & (df['overallTime'] > pd.Timedelta('3:20:00')) & (df['raceName'].str.contains("70.3")))]
    
    return pd.concat([a, b])

def filter_by_ag(df:pd.DataFrame, div:Division):
    #Filtering the age range
    return df[df['currentAge'].between(div.lowAge, div.highAge)]

def filter_by_name(df:pd.DataFrame, name:str):
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    div = Division(male=True, lowAge=30, highAge=34)
    matches = FindAthletes("athletes/upcoming_races/lp703.csv", div).find_matches()

    print(matches[['name', 'overallTime', 'raceName', 'raceDate']])
    print(matches[matches['name'].str.contains("Ele")])

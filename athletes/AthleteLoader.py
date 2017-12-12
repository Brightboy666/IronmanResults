import csv
import os

from fuzzywuzzy import fuzz
from athletes.Results import Division

import logging

import re
import datetime

logger = logging.getLogger(__name__)

import pandas as pd

class Results:
    def __init__(self):
        self.results_cache = None
        tmp_cache = []
        for df in self.__init_results__():
            tmp_cache.append(df)
        self.results_cache = pd.concat(tmp_cache)

    def get_results(self) -> pd.DataFrame:
        return self.results_cache

    def __init_results__(self):
        resultsDir = 'races/results'
        files = (x for x in os.listdir(resultsDir) if (str(x).endswith(".csv")))# and ("70.3-a" in str(x))))

        master_df = None

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

                self.__enrich_dataframe__(div_df, file)

                yield div_df
            except Exception as e:
                logger.exception("Had an issue with: {}".format(file))
                logger.exception(e)

    def __enrich_dataframe__(self, tmp_df, file):
        #Setting times for these peeps as beng very slow
        tmp_df.ix[tmp_df.overallTime.isin(['DNS', 'DNF', 'DQ', '---', pd.np.nan]), 'overallTime'] = "19:59:59"
        tmp_df['overallTime'] = pd.to_timedelta(tmp_df['overallTime'])

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
        tmp_df.fillna("MISSIING DATA", inplace=True)
#Takes a csv file version of the bib list and reorders it.

import pandas as pd
from Reformatter import CSV2AthleteList
import os
import logging
import datetime

from fuzzywuzzy import process, fuzz
import re

logger = logging.getLogger(__name__)

class Division(object):
    def __init__(self, male:bool, lowAge:int, highAge:int):
        self.male = male
        self.lowAge = lowAge
        self.highAge = highAge

    def toAGStr(self):
        sex = "M" if self.male else "F"
        divStr = "{}{}-{}".format(sex, self.lowAge, self.highAge)
        return divStr

class FindAthletes(object):
    def __init__(self, input_csv:str, division:Division):
        self.input_csv = input_csv
        self.division = division

    def find_matches(self):
        print("Finding athletes for upcoming race: {}".format(self.input_csv))
        upcoming_athletes = CSV2AthleteList(self.input_csv).df()
        upcoming_athletes = upcoming_athletes[upcoming_athletes['Division'] == self.division.toAGStr()]

        print("Finding race results for {}".format(self.division.toAGStr()))
        prev_results = self.get_results_for_ag(self.division)

        print("Finding matches")

        def fuzzy_match(x):
            full_name = x['Full Name']

            regex = ""
            for name_part in full_name.split(' '):
                regex += name_part[0] + ".*"

            try:
                smaller_list_athletes = prev_results[prev_results['name'].str.contains(re.compile(regex)).fillna(True)]

                smaller_list_athletes = smaller_list_athletes[smaller_list_athletes['name'].notnull()]

                m = process.extractOne(x['Full Name'], choices=smaller_list_athletes['name'], scorer=fuzz.ratio, score_cutoff=70)

                if m is None:
                    match_score = 0
                    match_name = ""
                else:
                    match_score = m[1]
                    match_name = m[0]

                x['Score'] = match_score
                x['Match Name'] = match_name

                return x
            except Exception as e:
                logging.exception(x)
                logging.exception(regex)
                logging.exception(e)
                #fuzzy_match(x)

        r = upcoming_athletes.apply(fuzzy_match, axis=1)
        upcoming_athletes_with_old_results = r[(r['Score'].notnull()) & (r['Score']>80)] #80 appears to be a good cutoff to avoid having too many false matches

        matching_old_results = prev_results[prev_results['name'].isin(upcoming_athletes_with_old_results['Match Name'])]

        return matching_old_results

    def get_results_for_ag(self, div:Division):
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
                tmp_df = pd.DataFrame.from_csv(csv_location, header=1)

                if(len(tmp_df) < 10):
                    logger.debug("{} likely to be an empty race".format(csv_location))
                    continue

                self.enrich_dataframe(tmp_df, file)

                #Filtering the age range
                div_df = tmp_df[tmp_df['currentAge'].between(div.lowAge, div.highAge)]

                #Setting times for these peeps as beng very slow
                div_df.ix[div_df.overallTime.isin(['DNS', 'DNF', 'DQ', '---', pd.np.nan]), 'overallTime'] = "19:59:59"
                div_df['overallTime'] = pd.to_timedelta(div_df['overallTime'])

                #We're removing athletes with slow times because we're not going to need to look at them
                #for predicting who is worth watching at an upcoming race.
                b = div_df.ix[((div_df['overallTime'] < pd.Timedelta('11:45:00')) & (div_df['overallTime'] > pd.Timedelta('07:20:00')) & (~div_df['raceName'].str.contains("70.3")))]
                c = div_df.ix[((div_df['overallTime'] < pd.Timedelta('5:45:00')) & (div_df['overallTime'] > pd.Timedelta('3:20:00')) & (div_df['raceName'].str.contains("70.3")))]
                
                div_df = pd.concat([b,c])

                master_df = div_df if master_df is None else pd.concat([master_df, div_df])
            except Exception as e:
                logger.exception("Had an issue with: {}".format(file))
                logger.exception(e)

        return master_df

    def enrich_dataframe(self, tmp_df, file):
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    div = Division(male=True, lowAge=30, highAge=34)
    matches = FindAthletes("athletes/lp703.csv", div).find_matches()

    print(matches[['name', 'overallTime', 'raceName', 'raceDate']])
    print(matches[matches['name'].str.contains("Ele")])

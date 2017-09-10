#Takes a csv file version of the bib list and reorders it.

import pandas as pd
from Reformatter import CSV2AthleteList
import os
import logging

from fuzzywuzzy import process, fuzz

logger = logging.getLogger(__name__)

#Assumes this format:
#703,BEAULIEU,LAURENCE,F18-24,CAN
class FindAthletes(object):
    def __init__(self, input_csv, division):
        self.input_csv = input_csv
        self.division = division

    def find_matches(self):
        print("Finding athletes for upcoming race: {}".format(self.input_csv))
        upcoming_athletes = CSV2AthleteList(self.input_csv).df()
        upcoming_athletes = upcoming_athletes[upcoming_athletes['Division'] == self.division]

        #TMP TODO REMOVE
        import re
        upcoming_athletes = upcoming_athletes[upcoming_athletes['Full Name'].str.contains("Scott|Justin", flags=re.IGNORECASE)]

        print("Finding race results for {}".format(self.division))
        prev_results = self.get_results_for_ag("TODO FIGURE OUT DIVISION PARAMS")

        print("Finding matches")

        def fuzzy_match(x):
            m = process.extractOne(x['Full Name'], choices=prev_results['name'], scorer=fuzz.ratio, score_cutoff=80)

            if "JUSTIN SCOTT" in x['Full Name']:
                print(x['Full Name'])

            if m is None:
                match_score = 0
                match_name = ""
            else:
                match_score = m[1]
                match_name = m[0]

            x['Score'] = match_score
            x['Match Name'] = match_name

            return x


        r = upcoming_athletes.apply(fuzzy_match, axis=1)

        print(prev_results[prev_results['Match']>80])


    def get_results_for_ag(self, todo_params):
        resultsDir = '../races/results'
        files = (x for x in os.listdir(resultsDir) if str(x).endswith(".csv") and "timberman" in str(x))

        div_list = []

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

                #Changing values that aren't valid ages to 0 so they don't match
                #the following filter
                tmp_df.ix[tmp_df.age.isin(['---', pd.np.nan]), 'age'] = 0
                tmp_df['age'] = tmp_df['age'].astype(int)

                #Filtering the age range
                div_df = tmp_df[tmp_df['age'].between(32, 39)]
                div_list.append(div_df)

                #print(div_df)
            except Exception as e:
                logger.exception(e)

        a = pd.concat(div_list)

        #Setting times for these peeps as beng very slow
        a.ix[a.overallTime.isin(['DNS', 'DNF', 'DQ', pd.np.nan]), 'overallTime'] = "19:59:59"
        a['overallTime'] = pd.to_timedelta(a['overallTime'])

        #b = df[a['overallTime'] < pd.Timedelta('04:50:00')]
        #Having big windows right now to have more name matches to test fuzzy matching
        #TODO Have filters as a configurable item
        b = a.ix[((a['overallTime'] < pd.Timedelta('11:45:00')) & (a['overallTime'] > pd.Timedelta('07:20:00')))]
        c = a.ix[((a['overallTime'] < pd.Timedelta('5:45:00')) & (a['overallTime'] > pd.Timedelta('3:20:00')))]
        d = pd.concat([b, c])

        return d

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    FindAthletes("lp703.csv", "M35-39").find_matches()

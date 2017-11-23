#Takes a csv file version of the bib list and reorders it.

import pandas as pd
from Reformatter import CSV2AthleteList
import athletes.AthleteLoader as loader

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
        prev_results = loader.get_results_for_ag(self.division)

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
                logging.exception(e)

        r = upcoming_athletes.apply(fuzzy_match, axis=1)
        
        upcoming_athletes_with_old_results = r[(r['Score'].notnull()) & (r['Score']>80)] #80 appears to be a good cutoff to avoid having too many false matches
        matching_old_results = prev_results[prev_results['name'].isin(upcoming_athletes_with_old_results['Match Name'])]

        return matching_old_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    div = Division(male=True, lowAge=30, highAge=34)
    matches = FindAthletes("athletes/upcoming_races/im_phillipines_out_F2529.csv", div).find_matches()

    pd.options.display.max_rows = 999
    print(matches[['name', 'overallTime', 'raceName', 'raceDate']])

    matches[['name', 'overallTime', 'raceName', 'raceDate']].to_csv('athletes/upcoming_races/im_phil_to_watch_F2529.csv')

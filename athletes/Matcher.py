#Takes a csv file version of the bib list and reorders it.

import pandas as pd
from Reformatter import CSV2AthleteList
import os
import logging

logger = logging.getLogger(__name__)

#Assumes this format:
#703,BEAULIEU,LAURENCE,F18-24,CAN
class FindAthletes(object):
    def __init__(self, input_csv, division):
        self.input_csv = input_csv
        self.division = division

    def find_matches(self):
        df = CSV2AthleteList(self.input_csv).df()

        resultsDir = '../races/results'
        files = (x for x in os.listdir(resultsDir) if str(x).endswith(".csv"))

        div_list = []

        for file in files:
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
                div_df = tmp_df[tmp_df['age'].between(35, 39)]
                div_list.append(div_df)

                #print(div_df)
            except Exception as e:
                logger.exception(e)
                print("")

        all_div_results = pd.concat(div_list)

        print("Now lets compare results")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    FindAthletes("lp703.csv", "F25").find_matches()

#Takes a csv file version of the bib list and reorders it.

import pandas as pd

#Assumes this format:
#703,BEAULIEU,LAURENCE,F18-24,CAN
class CSV2AthleteList(object):
    def __init__(self, input_csv):
        self.input_csv = input_csv

    def __skip__(self, x):
        print(x)

    def df(self):
        #First we search for the first column that looks like headers
        start_row=-1
        with open(self.input_csv, mode='r', encoding="utf-8") as f:
            i = 0
            for line in f:           
                if "BIB" in line and "NAME" in line:
                    start_row = i
                    break
                i = i + 1

        #We read in the frame from the point we found above. 
        #This should mean we have 
        df = pd.DataFrame.from_csv(self.input_csv, header=i)
        df.columns = ['Last Name', 'First Name', 'Division', 'Country']

        df['Full Name'] = df['First Name'] +' '+ df['Last Name']
        return df

if __name__ == "__main__":
    df = CSV2AthleteList('lp703.csv').df()

    print(df)

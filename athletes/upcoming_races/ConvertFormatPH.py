import pandas as pd
import numpy as np
import os


print(os.getcwd())
df = pd.DataFrame.from_csv('athletes/upcoming_races/im_phillipines_input_F2529.csv').reset_index()
print(df.head())

df['name'] = df['First Name'] +' '+ df['Last Name']
df['ag'] = np.where(df['Gender'].str.startswith("M"), 'M'+df['Age Group'], 'M'+df['Age Group'])

df.reset_index()[['name', 'ag', 'Country']].to_csv('athletes/upcoming_races/im_phillipines_out_F2529.csv', index=False)
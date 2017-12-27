import pandas as pd

from athletes.Results import Division

if __name__ == "__main__":
    df = pd.DataFrame.from_csv("http://localhost:8080/all")

    print(df.head())
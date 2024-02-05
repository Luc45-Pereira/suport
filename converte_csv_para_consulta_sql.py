import pandas as pd

df = pd.read_csv('mpn.csv')

mpns = df['mpn'].to_list()
print(mpns)
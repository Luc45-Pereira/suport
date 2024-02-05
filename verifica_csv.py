import pandas as pd

df = pd.read_csv('manuais.csv')

external_ids = []

for i in df['manuais']:
    external_ids.append(i)

print(external_ids)
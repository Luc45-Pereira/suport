import pandas as pd

df = pd.read_csv('ads.csv')

new_df = pd.DataFrame()

new_df['external_id'] = df['external_id']
new_df['mpn'] = df['mpn']

new_df.to_csv('anuncios.csv', index=False, sep=';')
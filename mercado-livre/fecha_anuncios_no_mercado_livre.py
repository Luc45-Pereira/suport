# pausa anúncios de um csv de anúncios que não estão no mercado livre
import pandas as pd
import requests
import json
import time

url = 'https://api.mercadolibre.com/items/MLB123456789'
# token = 'APP_USR-5417402069385811-073013-9c6a93c0ecd16a4d208bf1e5e496b597-420633425'

# lê o csv
df = pd.read_csv('ads.csv')

# cria uma lista com os ids dos anúncios
ids = df['external_id'].tolist()

# cria um dataframe para armazenar os resultados
data_frame_result = pd.DataFrame(columns=['id', 'status', 'amount', 'updated_at'])

# cria um dataframe para armazenar os erros
data_frame_error = pd.DataFrame(columns=['id', 'status', 'amount', 'updated_at', 'error'])

# cria uma lista para armazenar os ids dos anúncios que não estão no mercado livre
adsNotActiveIds = []

# pausa os anúncios no mercado livre
for id in ids:
    try:
        url = f'https://api.mercadolibre.com/items/{id}?access_token=APP_USR-5417402069385811-101009-30b3624d02bed5053f811276d3758be8-553373958'
        json = {'status': 'paused', 'available_quantity': 0}
        response = requests.put(url, json=json)
    except:
        print('Erro ao buscar anúncio no ML')
        data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': ['Erro ao buscar anúncio no ML'], 'amount': [''], 'updated_at': [''], 'error':[response]})], axis=0)
        continue
    if response.status_code == 404:
        print('Anúncio não encontrado no ML')
        data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': ['Anúncio não encontrado no ML'], 'amount': [''], 'updated_at': [''], 'error':[response.json()]})], axis=0)
        continue

    if response.status_code == 429:
        # espera 20 segundos e tenta novamente
        print('Erro 429: muitas requisições')
        time.sleep(20)
        try:
            url = f'https://api.mercadolibre.com/items/{id}?access_token=APP_USR-5417402069385811-101009-30b3624d02bed5053f811276d3758be8-553373958'
            json = {'status': 'paused', 'available_quantity': 0}
            response = requests.put(url, json=json)
        except:
            print('Erro ao buscar anúncio no ML')
            data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': ['Erro ao buscar anúncio no ML'], 'amount': [''], 'updated_at': [''], 'error':[response.json()]})], axis=0)
            continue

    if response.status_code != 200:
        print('Erro ao pausar anúncio no ML')
        data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': ['Erro ao pausar anúncio no ML'], 'amount': [''], 'updated_at': [''], 'error': [response.json()]})], axis=0)
        continue

    response = response.json()
    if 'status' in response:
        print('status do anúncio: ', response['status'])
        if response['status'] == 'paused':
            print('Anúncio pausado')
            print('Quantidade: ', response['available_quantity'])
        data_frame_result = pd.concat([data_frame_result, pd.DataFrame({'id':[id], 'status': [response['status']], 'amount': [response['available_quantity']], 'updated_at': [response['last_updated']]})], axis=0)
    else:
        data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': [response], 'amount': [''], 'updated_at': ['']})], axis=0)
        adsNotActiveIds.append(id)

# salva os resultados em csv
data_frame_result.to_csv('resultpaused.csv', index=False)
data_frame_error.to_csv('errorpaused.csv', index=False)

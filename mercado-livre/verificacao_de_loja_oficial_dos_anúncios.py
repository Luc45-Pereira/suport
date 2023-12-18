import requests
import pandas as pd

def getAdFromML(id, token):
    print('Buscando anúncio no ML')
    url = f'https://api.mercadolibre.com/items/{id}'
    response = requests.get(url)
    return response.json()

def getIdsFromCSV():
    print('Lendo ids do csv')
    df = pd.read_csv('ids.csv')
    df = df[['external_id']]
    return df['external_id'].tolist()

def verify_official_store(response):
    print('verificando se é loja oficial')
    if 'official_store_id' in response:
        
        if 	1604 == response['official_store_id']:
            print('é loja oficial')
            return True
    else:
        return False

def main():
    ids = getIdsFromCSV()

    adsInStore = []
    adsNotInStore = []
    adsNotInStoreIds = []
    for id in ids:
        response = getAdFromML(id, '')
        if verify_official_store(response):
            adsInStore.append(id)
        else:
            adsNotInStoreIds.append(id)
            adsNotInStore.append(id)
    print('Anúncios na loja: ', len(adsInStore))
    print('Anúncios não na loja: ', len(adsNotInStore))
    print('Anúncios não na loja: ', adsNotInStoreIds)

if __name__ == '__main__':
    main()
import pandas as pd
import requests
import json


def getAdFromML(id, token):
    print('Buscando anúncio no ML')
    try:
        url = f'https://api.mercadolibre.com/items/{id}?access_token=APP_USR-5417402069385811-082513-1e94ce03f61c8c0140e50dbb34976323-397531057'
        response = requests.get(url)
    except:
        print('Erro ao buscar anúncio no ML')
        return False
    return response.json()

def getIdsFromCSV():
    print('Lendo ids do csv')
    df = pd.read_csv('ids.csv')
    df = df[['external_id']]
    return df['external_id'].tolist()

def verify_status_ad(response):
    print('verificando status do anúncio')
    if 'status' in response:
        print('status do anúncio: ', response['status'])
        return response['status']
    else:
        return False

def create_data_frame_result():
    data_frame_result = pd.DataFrame(columns=['id', 'status', 'amount', 'updated_at'])
    return data_frame_result

def insert_in_csv_data_frame_result(data_frame_result, id, status, amount = '', updated_at = ''):
    data_frame_result = pd.concat([data_frame_result, pd.DataFrame({'id':[id], 'status': [status], 'amount': [amount], 'updated_at': [updated_at]})], axis=0)
    return data_frame_result

def main():
    ids = getIdsFromCSV()
    data_frame_result = create_data_frame_result()
    data_frame_error = create_data_frame_result()
    adsActive = []
    adsNotActive = []
    adsNotActiveIds = []
    for id in ids:
        response = getAdFromML(id, '')
        if response == False:
            data_frame_error = insert_in_csv_data_frame_result(data_frame_error, id, 'Erro ao buscar anúncio no ML')
            continue
        status = verify_status_ad(response)
        amount = response['available_quantity']
        updated_at = response['last_updated']
        if status:
            if status == 'active':
                print('Anúncio ativo')
                print('Quantidade: ', amount)
            data_frame_result = insert_in_csv_data_frame_result(data_frame_result, id, status, amount, updated_at)
        else:
            data_frame_error = insert_in_csv_data_frame_result(data_frame_error, id, response)
            adsNotActiveIds.append(id)
            adsNotActive.append(id)
    data_frame_result.to_csv('result.csv', index=False)
    data_frame_error.to_csv('error.csv', index=False)
    print('Anúncios ativos: ', len(adsActive))
    print('Anúncios não ativos: ', len(adsNotActive))
    print('Anúncios não ativos: ', adsNotActiveIds)

if __name__ == '__main__':
    main()
import requests
import pandas as pd


URL = 'https://api.mercadolibre.com/items/'
ACCESS_TOKEN = 'APP_USR-5417402069385811-082513-1e94ce03f61c8c0140e50dbb34976323-397531057'

def getAdFromML(id):
    url = f'{URL}{id}?access_token={ACCESS_TOKEN}'
    response = requests.get(url)
    if response.status_code != 200:
        print('Erro ao buscar anúncio no ML')
        return False
    
    return response.json()

def get_ids_from_CSV():
    df = pd.read_csv('ids.csv')
    df = df[['external_id']]
    return df['external_id'].tolist()

def get_status_ad(response):
    if 'status' in response:
        return response['status']
    else:
        return False

def get_available_quantity(response):
    if 'available_quantity' in response:
        return response['available_quantity']
    else:
        return False

def get_last_updated(response):
    if 'last_updated' in response:
        return response['last_updated']
    else:
        return False
    
def get_title(response):
    if 'title' in response:
        return response['title']
    else:
        return False

def get_price(response):
    if 'price' in response:
        return response['price']
    else:
        return False
    
def get_csv():
    df = pd.read_csv('ids.csv')
    return df
    
def verify_diferences_in_ads_and_csv(ad, csv):
    list_diferences = []
    if str(ad['status']).lower() != str(csv['status']).lower():
        list_diferences.append('status different')
    if ad['amount'] != csv['amount'] and csv['amount'] != 0 or ad['amount'] != csv['amount'] and ad['amount'] == 0 and ad['status'] != 'paused':
        list_diferences.append('amount different')
    if str(ad['title']).lower() != str(csv['title']).lower():
        list_diferences.append('title different')
    if int(ad['price']) != int(csv['price']):
        list_diferences.append('price different')
    if list_diferences:
        return list_diferences
    return 'equal'

def get_diferences_in_csv(csv, diference):
    diference_hub = {}
    if diference == 'equal':
        return 'equal'
    if 'status different' in diference:
        diference_hub['status'] = csv['status']
    if 'amount different' in diference:
        diference_hub['amount'] = csv['amount']
    if 'title different' in diference:
        diference_hub['title'] = csv['title']
    if 'price different' in diference:
        diference_hub['price'] = csv['price']
    return diference_hub


def main():
    ids = get_ids_from_CSV()
    data_frame_result = pd.DataFrame(columns=['id', 'status', 'amount', 'updated_at', 'title', 'price', 'diference', 'dados_hub'])
    data_frame_error = pd.DataFrame(columns=['id', 'status', 'amount', 'updated_at', 'title', 'price', 'diference', 'dados_hub'])
    adsActive = []
    adsNotActive = []
    adsNotActiveIds = []
    for id in ids:
        csv = pd.read_csv('ids.csv')
        response = getAdFromML(id)
        if response == False:
            data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': ['Erro ao buscar anúncio no ML'], 'amount': [''], 'updated_at': [''], 'title': [''], 'price': [''], 'diference': [''], 'dados_hub': ['']})], axis=0)
            continue
        status = get_status_ad(response)
        amount = get_available_quantity(response)
        updated_at = get_last_updated(response)
        title = get_title(response)
        price = get_price(response)
        ad = {'id': id, 'status': status, 'amount': amount, 'updated_at': updated_at, 'title': title, 'price': price}
        csv = csv.loc[csv['external_id'] == id]
        csv = csv.to_dict('records')[0]
        diference = verify_diferences_in_ads_and_csv(ad, csv)
        diference_hub = get_diferences_in_csv(csv, diference)
        if status:
            if status == 'active':
                print('Anúncio ativo')
                print('Quantidade: ', amount)

            data_frame_result = pd.concat([data_frame_result, pd.DataFrame({'id':[id], 'status': [status], 'amount': [amount], 'updated_at': [updated_at], 'title': [title], 'price': [price], 'difference': [diference], 'dados_hub': [diference_hub]})], axis=0)
        else:
            data_frame_error = pd.concat([data_frame_error, pd.DataFrame({'id':[id], 'status': [response], 'amount': [''], 'updated_at': [''], 'title': [''], 'price': [''], 'diference': [diference], 'dados_hub': [diference_hub]})], axis=0)
            adsNotActiveIds.append(id)

    data_frame_result.to_csv('result.csv', index=False)
    data_frame_error.to_csv('error.csv', index=False)

if __name__ == '__main__':
    main()
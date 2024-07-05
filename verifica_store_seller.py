import pandas as pd
import requests
import math

def verifyStoreSeller(token,seller_id, store_id):
    url = f'https://api.mercadolibre.com/users/{seller_id}/brands?access_token={token}'
    response = requests.get(url)
    ids_not_found = []
    text = 'Loja incorreta'
    user_type = 'normal'
    if response.status_code == 200:
        response = response.json()
        user_type = response['user_type']
        for brand in response['brands']:
            if brand['official_store_id'] == store_id:
                text = f'Loja {int(store_id)} correta'
            else:
                ids_not_found.append(brand['name'])
    else:
        if math.isnan(store_id):
            ids_not_found = ['Perfil do vendedor']
            text = f'Loja correta'

    return ids_not_found, text, user_type


def getSellerCsv():
    df = pd.read_csv('tokens.csv')
    return df

def main():
    df = getSellerCsv()
    df_result = pd.DataFrame(columns=['Seller', 'loja oficial atual', 'loja esta correta?', 'lojas encontrada para o seller no MELI'])
    for index, row in df.iterrows():
        if row['store_name'] == 'Grupo Barigui Loja Oficial':
            continue
        print(f'Verificando {row["name"]}')
        if math.isnan(row['external_id']):
            print(f'Não possui loja')
            store = 'perfil do vendedor'
        else:
            store = int(row['external_id'])
            print(f'Loja: {store}')
        ids, text, user_type = verifyStoreSeller(row['access_token'], row['seller_id'], row['external_id'])
        df_result = pd.concat([df_result, pd.DataFrame({'Seller': [row['name']], 'tipo': [user_type], 'loja oficial atual': [row['store_name']], 'loja esta correta?': [text], 'lojas encontrada para o seller no MELI': [ids]})], ignore_index=True)

    df_result.to_csv('result.csv', index=False)

    return

if __name__ == '__main__':
    main()
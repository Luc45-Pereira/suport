import aiohttp
import asyncio
import pandas as pd

DEFAULT_URL = "https://api.mercadolibre.com"
# https://api.mercadolibre.com/users/1210093583/items/search?access_token=APP_USR-5417402069385811-041707-7dc33bf6f692cb8234faf22b012d7123-1210093583&category=MLB22664&q=Calota%20Central%20Da%20Roda%20Fiat%20Uno%20%C3%9Altimas%20Unidades

class Manager():
    url = f"{DEFAULT_URL}"
    token = None
    results = []
    total = True
    offset = 0
    results_per_seller = pd.DataFrame()

    def __init__(self, token):
        self.token = token
        self.results = []
        self.total = True
        self.offset = 0
    
    async def get_ads_from_route(self, session, offset, limit, seller_id, seller_sku, seller_ad, token, scroll_id=''):
        async with session.get(f'{self.url}/users/{seller_id}/items/search?access_token={token}&sku={seller_sku}', ssl=False) as response:
            if 200 == response.status:
                response_json = await response.json()
                
                if 'results' in response_json:
                    if len(response_json['results']) > 1:
                        for ad in response_json['results']:
                            print(ad, seller_ad)
                            if ad != seller_ad:
                                return ad

            else:
                return None     


def get_tokens():
    tokens_and_users = pd.read_csv('tokens.csv')
    tokens = tokens_and_users['access_token'].tolist()
    users = tokens_and_users['user_id'].tolist()
    return tokens, users

def get_ads_seller(seller_id):
    ads = pd.read_csv('ads.csv')
    print(ids := ads['seller_sku'].to_list())
    ads = ads['external_id'].to_list()
    # ids = ads['seller_sku'].to_list()

    return ads, ids


async def get_duplicated(manager, ids, index, user, seller_sku, ad,token, result_duplicated):
    async with aiohttp.ClientSession() as session:
        try:
            get_duplicated = await manager.get_ads_from_route(session, 0, 50, user, seller_sku, ad, token)

            if get_duplicated:
                result_duplicated = pd.concat([result_duplicated, pd.DataFrame({
                    'seller_sku': [seller_sku],
                    'state': ['duplicated'],
                    'ad': [get_duplicated]
                })], ignore_index=True)
        except Exception as e:
            print(f"Error: {e}")
    return result_duplicated

async def main():
    tokens, users = get_tokens()
    
    for token, user in zip(tokens, users):
        print(f"Token: {token} - User: {user}")

        ads, ids = get_ads_seller(user)
        manager = Manager(token)
        results_per_seller = pd.DataFrame()
        result_duplicated = pd.DataFrame()

        tasks = []
        for ad, index in zip(ads, range(len(ads))):
            print(f"Ad: {ad} - Index: {index}")
            seller_sku = f"nvpc_ad_{ids[index]}"

            tasks.append(get_duplicated(manager, ids, index, user, seller_sku, ad, token, result_duplicated))
        
        get_duplicated_ads = await asyncio.gather(*tasks)

        result_duplicated_ads = pd.concat(get_duplicated_ads, ignore_index=True)

        result_state_unica = result_duplicated_ads[result_duplicated_ads['state'] == 'unica']
        result_state_orfao = result_duplicated_ads[result_duplicated_ads['state'] != 'unica']
        result_state_orfao.to_csv(f'{user}-result.csv', index=False, sep=';')
        result_state_unica.to_csv(f'{user}-result_unica.csv', index=False, sep=';')
        # results_per_seller.to_csv(f'{user}-results_per_seller.csv', index=False, sep=';')

if __name__ == '__main__':
    asyncio.run(main())
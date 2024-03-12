import asyncio
import aiohttp
import time
import argparse
import logging
import pandas as pd
from prefect import task, flow

DEAFAULT_URL = 'https://api.mercadolibre.com'
DAYS_AGO = 7
DEFAULT_TOKEN = 'APP_USR-8599480578339107-022215-d2ed4714d19c57bb80825e50b5568e77-310307361'

logging.basicConfig(level=logging.INFO, filename='./app.log')
logger = logging.getLogger()

class Manager():
    url = f"{DEAFAULT_URL}"
    token = None
    results = []
    total = True
    offset = 0

    def __init__(self, token):
        self.token = token
    
    async def get_infracoes(self, session, days_ago, o, limit, seller_id):
        self.offset = o
        while self.total:
            tasks = [self.get_from_route(session, offset, limit, seller_id) for offset in range(self.offset, self.offset + 25 * limit, limit)]
            await asyncio.gather(*tasks)
        return self.results
    
    async def get_from_route(self, session, offset, limit, seller_id):
        print(f"Offset: {offset} - Limit: {limit}")
        if not self.total:
            return []
        
        async with session.get(f'{self.url}/moderations/infractions/{seller_id}?limit={limit}&offset={offset}&filter_subgroup=PQT', ssl=False) as response:
            if 200 == response.status:
                logger.info(f"Get ads - Status: {response.status}")
                response_json = await response.json()
                # print(f"Response: {response_json} - url: {response.url}")

                if not response_json['infractions']:
                    self.total = True if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit']) else False
                    return
                
                for infraction in response_json['infractions']:
                    if infraction['related_item_id']:
                        logger.info(f"Infraction found: {infraction}")
                        self.results.append(infraction)
                self.offset += 20
                self.total = True if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit'] ) and offset < 5000 else False
                return
            else:
                response_json = await response.json()
                logger.error(f"Error: {response.status} - {response_json} - url: {response.url}")
                return 

@task
def cria_query_para_buscar_os_anuncios_com_problemas_na_imagem(infractions):
    for i in infractions:
        infraction_related_item_id = [str(x['related_item_id']) for x in i]
    # Adicionando aspas duplas ao redor de cada ID
    infraction_related_item_id = ['"' + x + '"' for x in infraction_related_item_id]

    sql = f"""
    SELECT * FROM marketplace_ad as ad 
    JOIN corporation_product_offer as offer on offer.id = ad.offer_id
    JOIN corporation_product as product on product.id = offer.company_produt_id
    JOIN catalog_product as catalog on catalog.id = product.catalog_product_id
    WHERE ad.id in ({','.join(infraction_related_item_id)})
    GROUP BY catalog.id
    """

    return sql

@task
async def busca_id_client_meli(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'{DEAFAULT_URL}/users/me', ssl=False) as response:
            if 200 == response.status:
                response_json = await response.json()
                return response_json['id']
            else:
                response_json = await response.json()
                logger.error(f"Error: {response.status} - {response_json} - url: {response.url}")
                return None

@task
def gera_csv_com_os_anuncios_com_problemas_na_imagem(infractions):
    df_infractions = pd.DataFrame()
    for i in infractions:
        df = pd.DataFrame(i)
        df_infractions = pd.concat([df_infractions, df])
    df_infractions.to_csv('infractions.csv', index=False)


@task
def le_csv_com_tokens():
    return pd.read_csv('ads.csv')


@flow(log_prints=True)
async def busca_anuncios_com_infracoes(token = None, days_ago = DAYS_AGO, offset = 0, limit = 20):
    initial_time = time.time()

    ads = le_csv_com_tokens()
    listagem = []
    invalid_tokens = []
    df_result = pd.DataFrame(columns=['ad_id', 'mpn', 'reason', 'remedy'])
    for i, token in ads.iterrows():
        try:
            # if len(listagem) > 5000:
            #     break

            if token[3] in invalid_tokens:
                continue
            seller_id = await busca_id_client_meli(token[3])

            if not seller_id:
                invalid_tokens.append(token[3])
                continue

            print(f"Token: {token[3]} - Seller ID: {seller_id} - linha: {i}")
            headers = {
                'Authorization': f'Bearer {token[3]}'
            }
            manager = Manager(token[3])
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f'{DEAFAULT_URL}/moderations/infractions/{seller_id}?related_item_id={token[0]}&filter_subgroup=PQT', ssl=False) as response:
                    if 200 == response.status:
                        response_json = await response.json()
                        if not response_json['infractions']:
                            continue
                        for infraction in response_json['infractions']:
                            df_result = pd.concat([df_result, pd.DataFrame({'ad_id':[token[0]], 'mpn': [token[2]], 'reason': [infraction['reason']], 'remedy': [infraction['remedy']]})], axis=0)
                        listagem.append(response_json['infractions'])
                        
                    else:
                        response_json = await response.json()
                        logger.error(f"Error: {response.status} - {response_json} - url: {response.url}")

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            continue
            
    df_result.to_csv('result.csv', index=False)
    return listagem
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Busca Anuncios com Infracoes')
    parser.add_argument('--token', type=str, help='Mercado Pago Token', required=False)
    parser.add_argument('--days_ago', type=int, help='Days ago', default=DAYS_AGO)
    parser.add_argument('--offset', type=int, help='Offset', default=0)
    parser.add_argument('--limit', type=int, help='Limit', default=20)
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(busca_anuncios_com_infracoes.serve(name='Busca Anuncios com Infracoes'))
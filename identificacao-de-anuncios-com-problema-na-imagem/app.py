import asyncio
import aiohttp
import requests
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
        self.results = []
        self.total = True
        self.offset = 0
        
    
    async def get_infracoes(self, session, days_ago, o, limit, seller_id):
        self.offset = o
        while self.total:
            tasks = [self.get_from_route(session, offset, limit, seller_id) for offset in range(self.offset, self.offset + 20 * limit, limit)]
            await asyncio.gather(*tasks)
        return self.results
    
    async def get_from_route(self, session, offset, limit, seller_id):
        if not self.total:
            return []
        
        async with session.get(f'{self.url}/moderations/infractions/{seller_id}?limit={limit}&offset={offset}', ssl=False) as response:
            if 200 == response.status:
                logger.info(f"Get ads - Status: {response.status}")
                response_json = await response.json()
                # print(f"Response: {response_json} - url: {response.url}")

                if not response_json['infractions']:
                    self.total = True if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit']) else False
                    return
                
                for infraction in response_json['infractions']:
                    if infraction['related_item_id']:
                        print(f"Infraction found: {infraction}, total: {response_json['paging']['total']}, offset: {response_json['paging']['offset']}, limit: {response_json['paging']['limit']}")
                        self.results.append(infraction)
                self.offset += 20
                self.total = True if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit'] ) and offset < 10000 else False
                print(f"Offset: {offset} - Limit: {limit} - total: {response_json['paging']['total']} - offset: {response_json['paging']['offset']} - limit: {response_json['paging']['limit']}")
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
    ads_id = pd.read_csv('anuncios.csv', sep=';')
    listagem = []
    invalid_tokens = []
    
    df_error = pd.DataFrame(columns=['ad_id', 'error'])
    for i, token in ads.iterrows():
        df_result = pd.DataFrame(columns=['ad_id', 'seller', 'mpn', 'reason', 'remedy'])
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
                results = await manager.get_infracoes(session, days_ago, offset, limit, seller_id)
                count_results = len(results)
                infraction_related_item_id = ''
                i = 0
                print(f"Results: {count_results}")
                items = {}

                for infraction in results:
                    items[infraction['related_item_id']] = items[infraction['related_item_id']] + 1 if infraction['related_item_id'] in items else 1
                    if items[infraction['related_item_id']] >= 5:
                        continue

                    try:
                        # async with session.get(f'{DEAFAULT_URL}/items/{infraction["related_item_id"]}', ssl=False) as response:
                        response = requests.get(f'{DEAFAULT_URL}/items/{infraction["related_item_id"]}?access_token={token[3]}')
                        print(f"Response: {response.status_code} - url: {response.url}")
                        is_nvpc_ad = 'nao' if infraction['related_item_id'] not in ads_id['external_id'].values else 'sim'

                        if 200 == response.status_code:
                            response_json = response.json()
                            if not response_json:
                                continue
                            print(f"Buscando atributo")
                            mpn = "Anúncio sem MPN"
                            if 'attributes' in response_json:
                                for attribute in response_json['attributes']:
                                    if attribute['id'] == 'MPN':
                                        mpn = attribute['value_name']
                                    elif attribute['id'] == 'PART_NUMBER':
                                        partnumber = attribute['value_name']
                                    continue
                                mpn = mpn if mpn != partnumber and mpn != "Anúncio sem MPN" else partnumber
                            suggestion = True
                            print(f"Buscando categorias")
                            if 'suggested' not in infraction:
                                suggestion = False
                                categories_suggested = "Sem sugestão de categoria"
                            print(f"Buscando categorias")
                            categories_suggested = "Sem sugestão de categoria"
                            if suggestion != False:
                                print(f"Buscando sugestão de categoria")
                                print(f"Infraction: {infraction['suggested']}")
                                print(f"Categorias: {infraction['suggested']['categories']}")
                                if 'categories' in infraction['suggested']:
                                    print(f"Categories: {infraction['suggested']['categories']}")
                                    categories_suggested = [x['path'] for x in infraction['suggested']['categories']]
                                # for suggested in infraction['suggested']:
                                #     print(f'ad_id: {infraction["related_item_id"]}')
                                #     print(f"Suggested: {suggested}")
                                #     categories_suggested = []
                                #     if 'categories' in suggested:
                                #         print(f"Categories: {suggested['categories']}")
                                #         for categories in suggested['categories']:
                                #             print(f"Categories: {categories}")
                                #             categories_suggested = [x['path'] for x in categories]
                                        
                                    if categories_suggested == []:
                                        categories_suggested = "Sem sugestão de categoria"

                            is_nvpc_ad = 'nao' if infraction['related_item_id'] not in ads_id['external_id'].values else 'sim'
                            if mpn == "Anúncio sem MPN" and is_nvpc_ad == 'sim':
                                mpn = ads_id.loc[ads_id['external_id'] == infraction['related_item_id'], 'mpn'].values[0]
                            print(f"Is_nvpc_ad: {is_nvpc_ad} Ad ID: {infraction['related_item_id']} - MPN: {mpn} - Reason: {infraction['reason']} - Remedy: {infraction['remedy']} - Suggested: {categories_suggested}")
                            
                            df_result = pd.concat([df_result, pd.DataFrame({'ad_id':[infraction['related_item_id']], 'seller_id': [infraction['user_id']],'anuncio_nvpc?':[is_nvpc_ad],'seller': [token[1]] ,'mpn': [mpn], 'reason': [infraction['reason']], 'remedy': [infraction['remedy']], 'suggestion': [categories_suggested]})], axis=0)
                        elif is_nvpc_ad == 'sim':
                            
                            mpn = ads_id.loc[ads_id['external_id'] == infraction['related_item_id'], 'mpn'].values[0]
                            df_result = pd.concat([df_result, pd.DataFrame({'ad_id':[infraction['related_item_id']], 'seller_id': [infraction['user_id']],'anuncio_nvpc?':[is_nvpc_ad],'seller': [token[1]] ,'mpn': [mpn], 'reason': [infraction['reason']], 'remedy': [infraction['remedy']], 'suggestion': ['Sem sugestão de categoria']})], axis=0)
                        else:
                            response_json = response.json()
                            logger.error(f"Error: {response.status_code} - {response_json} - url: {response.url}")
                            continue
                    except Exception as e:
                        df_error = pd.concat([df_error, pd.DataFrame({'ad_id':[infraction['related_item_id']],'error': [str(e)]})], axis=0)
                        logger.error(f"Exception occurred: {str(e)}")
                        continue
                    
                    infraction_related_item_id = infraction['related_item_id']
                    i += 1
                listagem.append(results)
            #     async with session.get(f'{DEAFAULT_URL}/moderations/infractions/{seller_id}?related_item_id={token[0]}', ssl=False) as response:
            #         if 200 == response.status:
            #             response_json = await response.json()
            #             if not response_json['infractions']:
            #                 continue
            #             for infraction in response_json['infractions']:
            #                 df_result = pd.concat([df_result, pd.DataFrame({'ad_id':[token[0]],'seller': [token[1]] ,'mpn': [token[2]], 'reason': [infraction['reason']], 'remedy': [infraction['remedy']]})], axis=0)
            #             listagem.append(response_json['infractions'])
                        
            #         else:
            #             response_json = await response.json()
            #             logger.error(f"Error: {response.status} - {response_json} - url: {response.url}")
            df_result.to_csv(f'{token[1]}.csv', index=False)
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            continue
            
    df_error.to_csv('error.csv', index=False)
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
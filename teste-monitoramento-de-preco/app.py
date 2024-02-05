import pandas as pd
import asyncio
import aiohttp
import time
import redis
import argparse

URL = 'https://api.mercadolibre.com/sites/MLB/search'
NICKNAMES = ["ACDelco", "AKTAMOTORSGASTAO", "ALCXIMPORTS"]
LIMIT = 50

parser = argparse.ArgumentParser()
parser.add_argument('--mpn', help='MPN to search')
parser.add_argument('--nicknames', help='Nicknames to search')
ARGS = parser.parse_args()


class Ad:
    def __init__(self, id, nick):
        self.id = id
        self.nick = nick
        self.mpn = None
        self.price = None

    def set_mpn(self, mpn):
        self.mpn = mpn
    
    def set_price(self, price):
        self.price = price


class Fetch_Ads:
    def __init__(self, limit=50):
        self.limit = limit
        self.offset = 0
        self.nickname = None
        self.ads = []
        self.total = True

    def set_nickname(self, nickname):
        self.nickname = nickname

    async def find_ads(self, session):
        while self.total and len(self.ads) < 1000:
            tasks = [self.fetch_ads(session, offset) for offset in range(self.offset, self.offset + 50 * self.limit, self.limit)]
            payments_verify = await asyncio.gather(*tasks)
        return payments_verify

    async def fetch_ads(self, session, offset):
        if not self.total or len(self.ads) >= 1000 or offset > 1000:
            return []
        
        async with session.get(f'{URL}?limit={self.limit}&nickname={self.nickname}&offset={offset}') as response:
            status_code = response.status
            if status_code == 200:
                response_json = await response.json()
                results = response_json['results']

                for result in results:
                    if len(self.ads) < 1000:
                        ad = Ad(result['id'], result['seller']['nickname'])
                        if ad not in self.ads:
                            self.ads.append(ad)

                self.offset += 50
                self.total = True if len(self.ads) < 1000 and self.offset < response_json['paging']['total'] else False
            else:
                return

    async def find_mpn(self, session):
        tasks = [self.fetch_ad(session, ad) for ad in self.ads]
        payments_verify = await asyncio.gather(*tasks)
        return payments_verify

    async def fetch_ad(self, session, ad):
        if not ad or ad.mpn is not None:
            return

        async with session.get(f'https://api.mercadolibre.com/items/{ad.id}') as response:
            status_code = response.status
            if status_code == 200:
                response_json = await response.json()
                if 'seller_custom_field' not in response_json:
                    for atributo in response_json['attributes']:
                        if atributo['id'] == 'MPN':
                            for ads in self.ads:
                                if ads.id == ad.id:
                                    ads.set_mpn(atributo['value_name'])
                                    ads.set_price(response_json['price'])
                else:
                    for ads in self.ads:
                                if ads.id == ad.id:
                                    ad.set_mpn(response_json['seller_custom_field'])
                                    ads.set_price(response_json['price'])

            else:
                return

async def find_mpns_and_insert_redis():
    mpn = ARGS.mpn
    nicknames = ARGS.nicknames
    # send for mpn in df  to redis
    r = redis.Redis(host='172.18.0.8', port=6379)
    prices = []
    nicknames = nicknames.split(',')
    if mpn:
        for nickname in nicknames:
            item = r.get(f'{nickname}{mpn}')
            if item:
                prices.append(item)
        if prices:
            print(prices)

    start_time = time.time()
    loop = asyncio.get_event_loop()
    df = pd.DataFrame()

    for nick in NICKNAMES:
        fetch_ads = Fetch_Ads()
        fetch_ads.set_nickname(nick)

        while fetch_ads.total:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                start_seller_time = time.time()
                ads = await fetch_ads.find_ads(session)
                medium_time = time.time()
                print(f"Tempo de execução: Busca anúncios {nick} {medium_time - start_seller_time} segundos")

                end_search_time = time.time()
                ads = await fetch_ads.find_mpn(session)
                print(f"Tempo de execução: Busca MPNs {end_search_time - medium_time} segundos")

                for ad in fetch_ads.ads:
                    df = pd.concat([df, pd.DataFrame({'id': [ad.id], 'mpn': [ad.mpn], 'price': [ad.price], 'nick': [ad.nick]})], axis=0)

    end_time = time.time()
    df.to_csv('ads.csv', index=False)
    print("exec")

    
    for index, row in df.iterrows():
        mpn = row['mpn']
        r.set(
            name=f'{row["nick"]}{row["mpn"]}',
            value=row['price']
        )

    item = r.get('AKTAMOTORSGASTAO0KL0210155')
    print(item)
        
    execution_time = end_time - start_time
    print(f"Tempo de execução: Total {execution_time} segundos")



if __name__ == '__main__':
    r = redis.Redis(host='172.18.0.8', port=6379)
    item = r.get('AKTAMOTORSGASTAO0KL0210155')
    print(item)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(find_mpns_and_insert_redis())

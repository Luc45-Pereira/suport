import pandas as pd
import requests

def getAdsSeller(scroll_id = ''):
    url = 'https://api.mercadolibre.com/users/279232205/items/search?search_type=scan&access_token=APP_USR-5417402069385811-102705-161f0a0b2ffd2317f0fa49c939644eee-279232205&scroll_id=' + scroll_id
    response = requests.get(url)
    response = response.json()

    return response['results'], response['scroll_id']
   
        


def getAdsFromCSV():
    df = pd.read_csv('mlb.csv')

    return df['external_id'].tolist()

class Ad:
    def __init__(self, mlb, status, amount):
        self.mlb = mlb
        self.status = status
        self.amount = amount



def verifyAds(response, ads):
    if 'results' in response:
        
        for result in response['results']:
            url = f'https://api.mercadolibre.com/items/{result}?access_token=APP_USR-5417402069385811-102705-161f0a0b2ffd2317f0fa49c939644eee-279232205'
            response = requests.get(url)
            response = response.json()

            ad = Ad(response['id'], response['status'], response['available_quantity'])
            ads.append(ad)   
    else:
        return False
    
def createDataFrameResult():
    dataFrameResult = pd.DataFrame(columns=['id', 'status', 'amount'])
    return dataFrameResult

def compareAds(adsSeller, adsCsv):
    for ad in adsSeller:
        if ad.mlb not in adsCsv:
            print('Anúncio não no csv: ', ad)
        else :
            adsSeller.remove(ad)
    return adsSeller
    
def main():
    adsSeller = getAdsSeller()
    print(adsSeller.count())
    adsSellerIds = []
    verifyAds(adsSeller, adsSellerIds)
    df = createDataFrameResult()

    adsCsv = getAdsFromCSV()
    adsSeller = compareAds(adsSellerIds, adsCsv)

    for ad in adsSeller:
        df = pd.concat([df, pd.DataFrame({'id':[ad.mlb], 'status': [ad.status], 'amount': [ad.amount]})], axis=0)
    df.to_csv('ads.csv', index=False)

if __name__ == '__main__':
    main()
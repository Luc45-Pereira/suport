import requests
import pandas as pd
import datetime
# import pycurl
import io
import json
import asyncio
import aiohttp

ACCESS_TOKEN = 'APP_USR-5417402069385811-101506-62b091a8cecc5c6c8b3c35d76f6465d1-537429925'

class Payment:
    id = None
    status = None
    date_created = None
    date_approved = None
    date_last_updated = None
    order_id = None
    end_date = None
    status_payment = None

    def __init__(self, id, status, date_created, date_approved, date_last_updated, order_id):
        self.id = id
        self.status = status
        self.date_created = date_created
        self.date_approved = date_approved
        self.date_last_updated = date_last_updated
        self.order_id = order_id
        self.end_date = datetime.datetime.strptime(date_created, '%Y-%m-%dT%H:%M:%S.%f%z') + datetime.timedelta(days=7)
    
    def set_status_payment(self, status):
        self.status_payment = status

    def get_parameters_to_csv(self):
        return {'payment_id': self.id, 'status_payment': self.status, 'status': self.status_payment, 'date_created': self.date_created, 'date_approved': self.date_approved, 'date_last_updated': self.date_last_updated, 'order_id': self.order_id}

def get_ads_ids():
    data_frame = pd.read_csv('./ads.csv')
    return data_frame['id']

def get_orders_by_seller(seller_id, offset = 0):
    url = f'https://api.mercadopago.com/v1/payments/search?range=date_created&begin_date=NOW-2DAYS&end_date=NOW-0DAYS&limit=50&access_token={ACCESS_TOKEN}&offset={offset}&sort=date_approved'
    #url = f'https://api.mercadolibre.com/orders/search?seller={seller_id}&order.date_created.from=2022-12-13T13:09:32.000-04:00&order.date_created.to=2022-12-14T13:09:32.000-04:00&limit=50&offset={offset}&access_token={ACCESS_TOKEN}'
    # url = f'https://api.mercadolibre.com/orders/2000004734763588?access_token={ACCESS_TOKEN}'
    print(url)
    payments = []
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        response_json = response.json()
        print('total')
        print(response_json['paging']['total'])
        if response_json['paging']['total'] > 0:
            for result in response_json['results']:
                print(result)
                payment = Payment(result['id'], result['status'], result['date_created'], result['date_approved'], result['date_last_updated'], result['order']['id'] if result['order'] else None)
                payments.append(payment)
            
            if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit']):
                payments = payments + get_orders_by_seller(seller_id, response_json['paging']['offset'] + response_json['paging']['limit'])

        # if response_json['paging']['total'] > 0:
        #     for result in response_json['results']:
        #         for payment in result['payments']:
        #             print(result['id'])
        #             if (result['id'] == 2000004734763588):
        #                 print(payment['id'])
        #                 payment = Payment(payment['id'], payment['status'], payment['date_created'], payment['date_approved'], payment['date_last_modified'], result['id'])
        #                 payments.append(payment)
            
        #     if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit']):
        #         payments = payments + get_orders_by_seller(seller_id, response_json['paging']['offset'] + response_json['paging']['limit'])
    print(len(payments))
    return payments

def get_order_id_by_ad_meli(seller_id, ad_id):
    url = f'https://api.mercadolibre.com/orders/search?seller={seller_id}&q={ad_id}&access_token={ACCESS_TOKEN}'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.status_code)
        response_json = response.json()
        print(response_json)
        if response_json['paging']['total'] > 0:
            for result in response_json['results']:
                payment = Payment(result['payments'][0]['id'], result['payments'][0]['status'], result['payments'][0]['date_created'], result['payments'][0]['date_approved'], result['payments'][0]['date_last_modified'], result['payments'][0]['order_id'])
                return payment

def get_seller_id():
    url = f'https://api.mercadolibre.com/users/me?access_token={ACCESS_TOKEN}'
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['id']
    else:
        print(response.status_code)
        return None

# def verify_payment_exist_in_search_payments(payments, offset = 0):
#     url = f'https://api.mercadopago.com/v1/payments/search?range=date_updated&begin_date=2023-09-01T09:09:32.000-04:00&end_date=2023-10-16T13:09:32.000-04:00&limit=50&access_token={ACCESS_TOKEN}&offset={offset}'
#     response = requests.get(url)
#     list_payments_verify = []
#     if response.status_code == 200:
#         response_json = response.json()
#         if response_json['paging']['total'] > 0:
#             for result in response_json['results']:
#                 for payment in payments:
#                     if payment.id == result['id'] and payment.status != result['status']:
#                         list_payments_verify.append(payment)
#                         break

#             print(response_json['paging']['total'])
#             if response_json['paging']['total'] > (response_json['paging']['offset'] + response_json['paging']['limit']):
#                 list_payments_verify = list_payments_verify + verify_payment_exist_in_search_payments(payments, response_json['paging']['offset'] + response_json['paging']['limit'])
                

#                 # list_payments_verify.append(verify_payment_exist_in_search_payments(payments, response_json['paging']['offset'] + response_json['paging']['limit']))
            
#             return list_payments_verify
#         else:
#             return list_payments_verify
#     else:
#         print(response.status_code)
#         return list_payments_verify

# def verify_payment_cache(payments, offset = 0):
#     payments_verify = []
#     for payment in payments:
#         url = f'https://api.mercadopago.com/v1/payments/{payment.id}?access_token={ACCESS_TOKEN}'

#         # Cria um objeto pycurl.Curl
#         c = pycurl.Curl()

#         # Seta a URL da solicitação
#         c.setopt(pycurl.URL, url)

#         # Seta o cabeçalho da solicitação
#         c.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(ACCESS_TOKEN)])

#         # Cria um buffer para armazenar a resposta
#         buffer = io.BytesIO()
#         c.setopt(pycurl.WRITEDATA, buffer)

#         # Executa a solicitação
#         c.perform()

#         # Recupera o código de status da resposta
#         status_code = c.getinfo(pycurl.HTTP_CODE)

#         # Fecha o objeto pycurl
#         c.close()

#         if status_code == 200:
#             # Decodifica a resposta JSON
#             response_json = json.loads(buffer.getvalue())

#             # Verifica se o status do pagamento é diferente do status armazenado em cache
#             if payment.status == response_json['status']:
#                 continue

#             print('diferentes')
#             payment.set_status_payment(response_json['status'])
#             payments_verify.append(payment)
#         else:
#             print(status_code)
#             continue
#     return payments_verify

async def fetch_payment(payment, session):
    url = f'https://api.mercadopago.com/v1/payments/{payment.id}?access_token={ACCESS_TOKEN}'
    
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    
    async with session.get(url, headers=headers) as response:
        status_code = response.status
        if status_code == 200:
            response_json = await response.json()

            if payment.status == response_json['status']:
                return None
            print(response_json['status'])

            payment_response = Payment(response_json['id'], response_json['status'], response_json['date_created'], response_json['date_approved'], response_json['date_last_updated'], response_json['order']['id'] if response_json['order'] else None)

            payment.set_status_payment(response_json['status'])
            return payment_response, payment
        else:
            print(status_code)

async def verify_payment_cache(payments):
    payments_verify = []
    print('verify_payment_cache')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [fetch_payment(payment, session) for payment in payments]
        results = await asyncio.gather(*tasks)
        print(results)
        for result in results:
            if result is not None:
                payments_verify.append(result)
                
    
    return payments_verify


# def verify_payment_cache(payments, offset = 0):
#     payments_verify = []
#     for payment in payments:
#         url = f'https://api.mercadopago.com/v1/payments/{payment.id}?access_token={ACCESS_TOKEN}'
#         response = requests.get(url)
#         if response.status_code == 200:
#             response_json = response.json()
#             if payment.status == response_json['status']:
#                 continue
#             print('diferentes')
#             payment.set_status_payment(response_json['status'])
#             payments_verify.append(payment)
#         else:
#             print(response.status_code)
#             continue
#     return payments_verify

    
def create_data_frame_result():
    data_frame_result = pd.DataFrame(columns=['payment_id', 'order_id', 'status_payment', 'status', 'date_created', 'date_approved', 'date_last_updated'])
    return data_frame_result

def insert_in_csv_data_frame(data_frame_result, payment_id, order_id, status_payment, status, date_created, date_approved, date_last_updated):
    data_frame_result = pd.concat([data_frame_result, pd.DataFrame({'payment_id' : [payment_id], 'order_id' : [order_id], 'status_payment' : [status_payment], 'status': [status], 'date_created' : [date_created], 'date_approved' : [date_approved], 'date_last_updated' : [date_last_updated]})], axis=0)

    # data_frame_result = data_frame_result.append({'product_id': product_id, 'payment_id': payment_id, 'order_id': order_id, 'status_payment': status_payment}, ignore_index=True)
    return data_frame_result

async def main():
    print('='*50)
    print('Verify payment problematics')
    print('='*50)

    data_frame_result = create_data_frame_result()

    print('Getting seller id ...')
    seller_id = get_seller_id()

    print('Getting orders by seller ...')
    payments = get_orders_by_seller(seller_id)

    print('Verify payment exist in search payments ...')
    payments_verify = await verify_payment_cache(payments)

    print(len(payments_verify))
    if len(payments_verify) > 0:
        for payment in payments_verify:
            print(f'Inserting in csv ...')
            
            parameters = payment[0].get_parameters_to_csv()
            parameters1 = payment[1].get_parameters_to_csv()
            data_frame_result = insert_in_csv_data_frame(data_frame_result, parameters['payment_id'], parameters['order_id'], parameters['status_payment'], parameters['status'], parameters['date_created'], parameters['date_approved'], parameters['date_last_updated'])
            data_frame_result = insert_in_csv_data_frame(data_frame_result, parameters1['payment_id'], parameters1['order_id'], parameters1['status_payment'], parameters1['status'], parameters1['date_created'], parameters1['date_approved'], parameters1['date_last_updated'])

    # print('Getting ads ids ...')
    # ads_ids = get_ads_ids()
    # for ad_id in ads_ids:

    #     print(f'Getting order id by ad id: {ad_id} ...')
    #     result = get_order_id_by_ad_meli(seller_id, ad_id)
    #     if result is not None:
    #         order_id, payment_id, payment_status, payment_date, payment_end_date = result

    #         if order_id:

    #             # verify payment exist in search payments, if not exist, insert in csv
    #             print(f'Verify payment exist in search payments ...')
    #             if not verify_payment_exist_in_search_payments(payment_id, payment_date, payment_end_date):
    #                 data_frame_result = insert_in_csv_data_frame(data_frame_result, ad_id, payment_id, order_id, payment_status)
    #     else:
    #         print("A função retornou None")
    print('Saving csv ...')
    data_frame_result.to_csv('./payments_problems.csv', index=False)
    print('Finish')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
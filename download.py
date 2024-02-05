# faz download de arquivos de uma url
import requests
import os

url = "https://api.mercadopago.com/v1/account/settlement-report/settlement-report-447466746-2023-08-17-092406.csv"
token = "APP_USR-5417402069385811-112007-f2bc3035f5639b1f1272839523d539f7-447466746"

headers = {
    "Authorization": "Bearer " + token
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open("settlement-report.csv", "wb") as f:
        f.write(response.content)
else:
    print("Erro ao fazer download do arquivo")
    print(response.status_code)
    print(response.text)
    print(response.headers)
    print(response.request.headers)
    print(response.request.url)
    print(response.request.body)
    print(response.request.method)

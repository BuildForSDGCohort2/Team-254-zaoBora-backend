
import requests

from datetime import datetime
import base64
from requests.auth import HTTPBasicAuth

import instance.config as keys 

#unformatted_time = datetime.now()
formatted_time = datetime.now().strftime("%Y%m%d%H%M%S")
#print(formatted_time)


data_to_encode = keys.business_ShortCode + keys.lipa_na_mpesa_passkey + formatted_time
encoded_string = base64.b64encode(data_to_encode.encode('utf-8'))
decoded_string = encoded_string.decode('utf-8')



  
consumer_key = keys.consumer_key
consumer_secret = keys.consumer_secret



api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
  
r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
  



json_response = r.json()
my_access_token = json_response['access_token']







def lipa_na_mpesa():

    access_token = my_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = { "Authorization": "Bearer %s" % access_token }
    request = {
        "BusinessShortCode": keys.business_ShortCode,
        "Password": decoded_string,
        "Timestamp":formatted_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA": keys.phone_number,
        "PartyB": keys.business_ShortCode,
        "PhoneNumber":keys.phone_number,
        "CallBackURL": "https://google.com/",
        "AccountReference": "123456",
        "TransactionDesc": "Pay Farm Products"
    }
    
    response = requests.post(api_url, json = request, headers=headers)
    
    print (response.text)
    
lipa_na_mpesa()
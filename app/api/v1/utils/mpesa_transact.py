#import mpesa library
import  requests
import json

from flask import  Flask,requests,render_template
from .user_view import v1

from config import (consumer_key,consumer_secret)
from app import  app as app


app.config["API_ENVIRONMENT"] = "sandbox" #sandbox or live
app.config["APP_KEY"] = consumer_key # App_key from developers portal
app.config["APP_SECRET"] = consumer_key #App_Secret from developers portal



class MpesaTransact():
    
    #Get mpesa access token
    def token():
        mpesa_auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


        data = (requests.get(mpesa_auth_url,auth = HTTPBasicAuth(consumer_key,consumer_secret))).json()
        return data['access_token']
        
    
    
    
    #Implement mpesa c2b api (customer to busines transaction)
    
    def c2b_transact():
        reg_data={"shortcode": "600364",
            "response_type": "Completed",
            "confirmation_url": base_url,
            "validation_url": base_url
        }
        v=mpesaapi.C2B.register(**reg_data)  # ** unpacks the dictionary
        ##use v to capture the response


        #This method allows you to test a mock payment and see the result so it can be avoided in production mode.
        test_data={"shortcode": "600364",
            "command_id": "CustomerPayBillOnline",
            "amount": "100",
            "msisdn": "254708374149",
            "bill_ref_number": "account"
        }
        new_v = mpesaapi.C2B.simulate(**test_data)  # ** unpacks the dictionary
        #use new_v to capture the response
        return new_v.json()

    
    def c2b_confirmation():
        #save the data
        request_data = request.data

        #Perform your processing here e.g. print it out...
        print(request_data)
    
    
    
    
    
    @app.route('/access_token',methods=["POST"])
    



    @app.route('/register_urls')
    def register():
        mpesa_endpoint = ""
        headers = {"Authorization":"Bearer %s" % ac_token()}
        
        json = {
            "ShortCode": "600383",
            "ResponseType": "Completed",
            "ConfirmationURL": base_url + "/c2b/confirm",
            "ValidationURL": base_url + "/c2b/validation"
        }
        response_data = requests.post(mpesa_endpoint,json = req_body,headers = headers)

        return response_data




    #check balance 
    balance=mpesaapi.Balance

    #Reverse mpesa
    reversal=mpesaapi.Reversal

    #transaction_status=mpesaapi.TransactionStatus
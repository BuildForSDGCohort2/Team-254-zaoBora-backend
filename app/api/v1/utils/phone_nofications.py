#Import the AfricasTalking SDK into your app
import africastalking

def sms_send():
    #Create your credentials
    username = "sandbox"
    apikey = "api_key goes here"

    #Initialize the SDK
    africastalking.initialize(username, apikey)

    #Get the SMS service
    sms = africastalking.SMS

    #Define some options that we will use to send the SMS
    recipients = ['Recipients phone numbers go here']
    message = 'Hello,Zaobora notifies you.Blink!'
    sender = "45676"

    #Send the SMS
    try:
        #Once this is done, that's it! We'll handle the rest
        response = sms.send(message, recipients, sender)
        print(response)
    except Exception as e:
        print(f"Houston, we have a problem {e}")


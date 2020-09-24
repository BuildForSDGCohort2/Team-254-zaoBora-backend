import africastalking 

class SmsNotify:
    def __init__(self):
		# Set your app credentials
	    self.username = "YOUR_USERNAME"
        self.api_key = "2b2ffa3bbe8e06d1327d295a6ca4e9c8814d5d7b04c9122f91ee9f7442c0bcd8git "

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def send(self):
            # Set the numbers you want to send to in international format
            recipients = ["+254713YYYZZZ", "+254733YYYZZZ"]

            # Set your message
            message = "I'm a lumberjack and it's ok, I sleep all night and I work all day";

            # Set your shortCode or senderId
            sender = "shortCode or senderId"
            try:
				# Thats it, hit send and we'll take care of the rest.
                response = self.sms.send(message, recipients, sender)
                print (response)
            except Exception as e:
                print ('Encountered an error while sending: %s' % str(e))


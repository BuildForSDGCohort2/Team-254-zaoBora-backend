import re
import string
from datetime import datetime
import phonenumbers
# from phonenumbers import carriers

class UserValidator:

    def __init__(self, data={}):
        self.data = data

    # helper methods for error handling
    def errorHandler(self, error_name):
        errors = {
            "first_name": "Your first name should be between 4 to 24 characters long!",
            "last_name": "Your last name should be between 4 to 24 characters long!",
            "username": "Your username should be between 4 to 24 characters long!",
            "email": "Invalid email address!",
            "password": "Weak password!",
            "phone_number": "Invalid phone number",
            "unmatching_pass": "Your passwords don't match!",
            "valid_fname": "please enter valid first name!",
            "is_farmer": "is_farmer only accepts boolean values!",
            "valid_lname": "please enter valid last name!",
            "valid_username": "please enter valid username!"
        }
        return errors[error_name]

    def check_fields(self, data, fields):
        for key in fields:
            try:
                data[key]
            except:
                return {
                    "error": 'You missed the {} key, value pair'.format(key),
                    "status": 400
                }

    # validator methods
    def signup_fields(self, data):

        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_farmer', 'username', 'password', 'confirm_password']

        return self.check_fields(data, fields)

    def login_fields(self, data):

        fields = ['email', 'password']

        return self.check_fields(data, fields)

    def valid_name(self):
        field_names = {
            'first_name': str(self.data['first_name']),
            'last_name': str(self.data['last_name']),
            'username': str(self.data['username'])
        }

        if not field_names['first_name'].isalpha():
            return self.errorHandler("valid_fname")
        elif not field_names['last_name'].isalpha():
            return self.errorHandler('valid_lname')
        elif isinstance(field_names['username'], int):
            return self.errorHandler('valid_username')

        for key, value in field_names.items():
            if len(value) < 3 or len(value) > 25:
                return self.errorHandler(key)

    def valid_email(self):
        reg_email = re.compile(
            r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

        if not re.match(reg_email, str(self.data['email'])):
            return self.errorHandler('email')

    def validate_password(self):
        reg_password = re.compile(
            r"^(?=\S{8,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])")

        if not re.match(reg_password, str(self.data['password'])):
            return self.errorHandler('password')

    def matching_password(self):
        if str(self.data['password']) != str(self.data['confirm_password']):
            return self.errorHandler('unmatching_pass')
    
    def valid_phone_number(self):
        try:
            input_number = self.data['phone_number']
            len(input_number) <= 12
            num = phonenumbers.parse(input_number, "KE")
            phonenumbers.is_valid_number(num)
        except:
    	    return self.errorHandler('phone_number')
    
    def valid_farmer_bool(self):
    	try:
    	    (self.data['is_farmer'] == "True") or (self.data['is_farmer'] == "False")
    	except:
    	    return self.errorHandler('is_farmer')



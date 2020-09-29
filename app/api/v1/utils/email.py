from flask_mail import Message, Mail
from flask import current_app, url_for, render_template_string
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature


mail = Mail()


def generate_verification_token(email):
    # Generate email verification token

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_verification_token(token, expiration=3600):
    # Confirm email verification token

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        # Set email to true here
    except SignatureExpired:
        return {
            "error": "The token has expired!",
            "status": 403
        }
    except BadTimeSignature:
        return {
            "error": "The token is invalid!",
            "status": 403
        }
    return email


def send_email(email, tokens, verification_email):
    # Send email verification link

    try:
        subject = "Please confirm your email"
        template = render_template_string(
            "<p>Welcome! Thanks for signing up. Please follow this link to activate your account:</p> <p><a href='{{ verification_email }}'>{{ verification_email }}</a></p> <br> <p>Thanks!</p>",
            verification_email=verification_email
        )
        msg = Message(
            subject,
            recipients=[email],
            html=template,
            sender=current_app.config['MAIL_USERNAME']
        )
        mail.send(msg)

        return {
            **tokens,
            "msg": "Email sent successfully",
            "email": email,
            "status": 200
        }
    except Exception as e:
        print('--> ',e)
        return {
            "msg": "Error sending email",
            "status": 400
        }

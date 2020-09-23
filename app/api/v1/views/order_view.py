from flask_jwt_extended import jwt_required
from flask import jsonify, Blueprint

from app.api.v1.utils import transact_mpesa


v1 = Blueprint('paymentv1', __name__, url_prefix='/api/v1')

# Lipa na mpesa route
@v1.route("/lipa_mpesa")
@jwt_required
def lipa():
    pay_online = transact_mpesa.lipa_na_mpesa()
    return pay_online
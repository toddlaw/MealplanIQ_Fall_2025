from flask import request, jsonify
import stripe
import os
from app import app

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/create-charge', methods=['POST'])
def create_charge():
    try:
        token = request.json.get('token')
        amount = request.json.get('amount')

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Example charge',
            source=token
        )
        return jsonify(charge), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400

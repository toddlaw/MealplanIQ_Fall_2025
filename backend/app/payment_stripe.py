from flask import request, jsonify
import stripe
import os
from app import app

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_charge(token, amount):
    try:
        charge = stripe.Charge.create(
            amount=amount,  # amount in cents
            currency='usd',
            description='Example charge',
            source=token
        )
        return jsonify(charge), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
    
def create_subscription(email, token, plan_id):
    # if plan not in ['yearly', 'monthly']:
    #     return jsonify(error='Invalid plan'), 400
    # plan_id = os.getenv(f'STRIPE_{plan.upper()}_SUBSCRIPTION_ID')

    try:
        customer = stripe.Customer.create(
            email=email,
            source=token
        )
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'plan': plan_id,
                },
            ]
        )
        return jsonify(subscription), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
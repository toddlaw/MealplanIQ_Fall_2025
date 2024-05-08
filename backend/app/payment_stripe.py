from flask import request, jsonify
import stripe
import os
from app import app

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# def create_charge(token, amount):
#     try:
#         charge = stripe.Charge.create(
#             amount=amount,  # amount in cents
#             currency='usd',
#             description='Example charge',
#             source=token
#         )
#         return jsonify(charge), 200
#     except stripe.error.StripeError as e:
#         return jsonify(error=str(e)), 400
    
def create_subscription(email, token, plan):
    if plan == 'monthly':
        plan_id = os.getenv('STRIPE_MONTHLY_SUBSCRIPTION_KEY')
    elif plan == 'yearly':
        plan_id = os.getenv('STRIPE_YEARLY_SUBSCRIPTION_KEY')
    else:
        return jsonify(error='Invalid plan ID'), 400
    
    try:
        existing_customers = stripe.Customer.list(email=email).data

        if existing_customers:
            customer = existing_customers[0]  
        else:
            customer = stripe.Customer.create(
                email=email,
                source=token 
            )
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {'plan': plan_id},
            ]
        )
        return jsonify(subscription), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
    
def cancel_subscription(subscription_id):
    try:
        stripe.Subscription.delete(subscription_id)
        return jsonify(success=True), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400

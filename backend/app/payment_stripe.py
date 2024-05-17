from flask import request, jsonify
import stripe
import os
from app import app
import datetime
from user_db.user_db import instantiate_database

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
    
def handle_checkout_session_completed(session, user_id):
    print("User ID From Firebase:", user_id)
    user_id = "300" # hard coded user ID for test purpose
    subscription_stripe_id = session['subscription']
    print("Subscription Stripe ID: ", subscription_stripe_id)

    # Make an API call to Stripe to retrieve the subscription object
    subscription = stripe.Subscription.retrieve(subscription_stripe_id)
    expiry_date = subscription['current_period_end']
    subscription_expiry_date = datetime.datetime.fromtimestamp(expiry_date).date()
    print("Subscription Expiry Date: ", subscription_expiry_date)

    # Map the product ID to the corresponding subscription_type_id
    product_id = subscription['plan']['product']
    subscription_type_id = 1 if product_id == os.getenv('STRIPE_MONTHLY_SUBSCRIPTION_KEY') else 2 if product_id == os.getenv('STRIPE_YEARLY_SUBSCRIPTION_KEY') else 3
    print("Subscription Type ID: ", subscription_type_id)

    db = instantiate_database()
    with db.db.cursor() as cursor:
        cursor.execute(
            "UPDATE user_subscription SET subscription_type_id = %s, subscription_stripe_id = %s, subscription_expiry_date = %s WHERE user_id = %s",
            (subscription_type_id, subscription_stripe_id, subscription_expiry_date, user_id)
        )
        db.db.commit()
    return jsonify(success=True), 200

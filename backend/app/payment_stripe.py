from flask import request, jsonify
import stripe
import os
from app import app
import datetime
from user_db.user_db import instantiate_database

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def handle_checkout_session_completed(session, user_id):
    print("User ID From Firebase:", user_id)
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

def handle_subscription_updated(subscription):
    subscription_stripe_id = subscription['id']
    expiry_date = subscription['current_period_end']
    subscription_expiry_date = datetime.datetime.fromtimestamp(expiry_date).date()

    product_id = subscription['plan']['product']
    subscription_type_id = 1 if product_id == os.getenv('STRIPE_MONTHLY_SUBSCRIPTION_KEY') else 2 if product_id == os.getenv('STRIPE_YEARLY_SUBSCRIPTION_KEY') else 3

    db = instantiate_database()
    with db.db.cursor() as cursor:
        cursor.execute(
            "SELECT user_id FROM user_subscription WHERE subscription_stripe_id = %s",
            (subscription_stripe_id,)
        )
        result = cursor.fetchone()
        user_id = result[0]

        cursor.execute(
            "UPDATE user_subscription SET subscription_type_id = %s, subscription_expiry_date = %s WHERE user_id = %s",
            (subscription_type_id, subscription_expiry_date, user_id)
        )
        db.db.commit()
    return jsonify(success=True), 200

def handle_subscription_deleted(subscription):
    subscription_stripe_id = subscription['id']
    print("Subscription Stripe ID: ", subscription_stripe_id)
    try:
        # stripe.Subscription.delete(subscription_stripe_id)
        db = instantiate_database()
        with db.db.cursor() as cursor:
            cursor.execute(
                "UPDATE user_subscription SET subscription_stripe_id = NULL, subscription_type_id = 3, subscription_expiry_date = NULL WHERE subscription_stripe_id = %s",
                (subscription_stripe_id,)
            )
            db.db.commit()

        return jsonify(success=True), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
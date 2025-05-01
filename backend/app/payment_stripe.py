from flask import request, jsonify
import stripe
import os
from app import app
import datetime
from user_db.user_db import instantiate_database

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def get_subscription_type_id_from_product_id(product_id):
    if product_id == os.getenv('STRIPE_MONTHLY_SUBSCRIPTION_KEY'):
        return 3
    elif product_id == os.getenv('STRIPE_QUARTERLY_SUBSCRIPTION_KEY'):
        return 4
    elif product_id == os.getenv('STRIPE_YEARLY_SUBSCRIPTION_KEY'):
        return 5
    else:
        return 1 

def handle_checkout_session_completed(session, user_id):
    print("User ID From Firebase:", user_id)
    subscription_stripe_id = session['subscription']
    customer_id = session['customer']
    print("Subscription Stripe ID: ", subscription_stripe_id)

    # Make an API call to Stripe to retrieve the subscription object
    subscription = stripe.Subscription.retrieve(subscription_stripe_id)
    expiry_date = subscription['current_period_end']
    subscription_expiry_date = datetime.datetime.fromtimestamp(expiry_date).date()
    print("Subscription Expiry Date: ", subscription_expiry_date)

    # Map the product ID to the corresponding subscription_type_id
    product_id = subscription['plan']['product']
    subscription_type_id = get_subscription_type_id_from_product_id(product_id)
    print("Subscription Type ID: ", subscription_type_id)

    db = instantiate_database()
    with db.db.cursor() as cursor:
        cursor.execute(
            "UPDATE user_subscription SET subscription_type_id = %s, subscription_stripe_id = %s, subscription_expiry_date = %s, stripe_customer_id = %s WHERE user_id = %s",
            (subscription_type_id, subscription_stripe_id, subscription_expiry_date, customer_id, user_id)
        )
        db.db.commit()
    return jsonify(success=True), 200

def handle_subscription_updated(subscription):
    subscription_stripe_id = subscription['id']
    expiry_date = subscription['current_period_end']
    subscription_expiry_date = datetime.datetime.fromtimestamp(expiry_date).date()

    product_id = subscription['plan']['product']
    subscription_type_id = get_subscription_type_id_from_product_id(product_id)

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
    
def create_trial_payment_and_subscription(data):
    print('Received Payment Data:', data)
    billing = data.get('billing_details', {})
    address = billing.get('address', {})

    # Create Customer
    customer = stripe.Customer.create(
        email=data.get('customer_email'),
        name=billing.get('name'),
        address=address,
    )

    # Attach PaymentMethod to Customer
    stripe.PaymentMethod.attach(
        data['payment_method'],
        customer=customer.id,
    )

    # Set default payment method
    stripe.Customer.modify(
        customer.id,
        invoice_settings={
            'default_payment_method': data['payment_method'],
        }
    )

    # Create InvoiceItem (for 2week paid trial)
    stripe.InvoiceItem.create(
        customer=customer.id,
        amount=int(data['price'] * 100),
        currency="usd",
        description="2-week paid trial"
    )

    # Create and pay invoice
    invoice = stripe.Invoice.create(
        customer=customer.id,
        collection_method="charge_automatically"
    )
    finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)

    # Create subscription for 3-month plan after 14day trial
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{'price': 'price_1RDbAT08iagEEr2StBVcQv0A'}],
        default_payment_method=data['payment_method'],
        trial_period_days=14
    )
    trial_end_date = datetime.datetime.fromtimestamp(subscription.trial_end).date()

    return {
        'invoice_id': finalized_invoice.id,
        'subscription_id': subscription.id,
        'customer_id': customer.id,
        'trial_end_date': trial_end_date.isoformat()
    }

def create_customer_portal_by_id(user_id, return_url="http://localhost:4200/dashboard"):
    db = instantiate_database()
    cursor = db.db.cursor()
    cursor.execute(
        "SELECT stripe_customer_id FROM user_subscription WHERE user_id = %s",
        (user_id,)
    )
    result = cursor.fetchone()

    if not result:
        return None, "Customer not found"

    customer_id = result[0]
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )
    return session.url, None

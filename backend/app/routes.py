from app import app
from flask import redirect, request, jsonify, send_from_directory
from flask_cors import CORS
from app.generate_meal_plan import gen_meal_plan
from app.payment_stripe import create_subscription, cancel_subscription, handle_checkout_session_completed, handle_subscription_deleted, handle_subscription_updated
from app.manage_user_data import *
from app.send_email import scheduled_email_test, scheduled_email_test_clicked_by_generation_button
from user_db.user_db import instantiate_database
import stripe

# Enable CORS for all domains on all routes
CORS(app)

# serve static files
@app.route('/', defaults={'path': ''}) 
@app.route('/<path:path>')
def index(path):
        if path:
            return send_from_directory('static', path)
        else:
            return send_from_directory('static', "index.html")
        
@app.route('/static/splash')
@app.route('/static/mission')
@app.route('/static/philosophy')
@app.route('/static/approach')
@app.route('/static/technology')
@app.route('/static/leadership')
@app.route('/static/timeline')
@app.route('/static/contact')
@app.route('/static/login')
@app.route('/static/sign-up')
@app.route('/static/profile')
@app.route('/static')
def static_files():
    return send_from_directory('static', 'index.html')

# redirect 404 to root URL
@app.errorhandler(404)
def page_not_found(e):
    print(request.path)
    return redirect('/')

@app.route('/create-subscription', methods=['POST'])
def handle_create_charge():
    email = request.json.get('email')
    token = request.json.get('token')
    plan_type = request.json.get('plan_type')
    return create_subscription(email, token, plan_type)

@app.route('/cancel-subscription', methods=['POST'])
def handle_cancel_subscription():
    subscription_id = request.json.get('subscription_id')
    return cancel_subscription(subscription_id)

@app.route('/signup', methods=['POST'])
def handle_signup():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    email = data.get('email')
    db = instantiate_database()
    result = db.insert_user_and_set_default_subscription_signup(user_id, user_name, email)
    return result

@app.route('/api', methods=['POST'])
def receive_data():
    data = request.json
  
    user_data = extract_user_profile_data_from_json(data)
    extract_data = extract_data_from_json(data)
    db = instantiate_database()
    user_name = 'Diane' # hard coded user name
    hard_coded_user_id = 300
    email = 'diane@test.ca' # hard coded user email

    db.insert_user_and_set_default_subscription_signup(hard_coded_user_id, user_name, email)
    db.update_user_profile(**user_data)
    process_user_data(db, hard_coded_user_id, extract_data)

    is_user_id_valid = db.check_user_id_existence(hard_coded_user_id)

    try:
        response = gen_meal_plan(data)
    except Exception as e:
        response = {'error': str(e)}
        print(f"Failed to generate meal plan: {str(e)}")
        
    email_sent_time = scheduled_email_test_clicked_by_generation_button(data, db, hard_coded_user_id)
    if is_user_id_valid:
        db.update_user_last_date_plan_profile(hard_coded_user_id, data['maxDate'])

    scheduled_email_test(email_sent_time, db, hard_coded_user_id)
    return jsonify(response)

endpoint_secret = 'whsec_d50a558aab0b7d6b048b21ec26aaf7aceeb99959c40d60d08d5973b76d6db560'

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            # change endpoint_secret to os.getenv('STRIPE_WEBHOOK_SECRET') when live mode
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print("ValueError: ", e)
        return jsonify(error='Invalid payload'), 400
    except stripe.error.SignatureVerificationError as e:
        print("SignatureVerificationError: ", e)
        return jsonify(error='Invalid signature'), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['client_reference_id']
        return handle_checkout_session_completed(session, user_id)
    else:
        print('Unhandled event type {}'.format(event['type']))
        return jsonify(success=True), 200

@app.route('/get_subscription_type', methods=['GET'])
def get_subscription_type():
    data = request.json
    user_id = data.get('user_id')
    db = instantiate_database()
    cursor = db.db.cursor()
    query = "SELECT subscription_type_id FROM user_subscription WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        subscription_type_id = result[0]
        return jsonify({'subscription_type_id': subscription_type_id})
    else:
        return jsonify({'error': 'User not found'}), 404

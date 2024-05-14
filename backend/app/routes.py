from flask import redirect, request, jsonify, send_from_directory
from app import app
from app.generate_meal_plan import gen_meal_plan
from app.payment_stripe import create_subscription, cancel_subscription, handle_checkout_session_completed
from user_db.user_db import instantiate_database
import stripe
# from app.send_email import scheduled_email_test


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
    print("Received data", request.json)
    data = request.json
    user_data = _extract_user_profile_data_from_json(data)
    extract_data = _extract_data_from_json(data)
    db = instantiate_database()
    db.update_user_profile(**user_data)
    _process_user_data(db, user_data['user_id'], extract_data)
    print("gen_meal_plan input data", data)
    is_user_id_valid = db.check_user_id_existence(user_data['user_id'])
    # is_user_subscription_valid = db.check_user_subscription_validity(user_data['user_id'])
    if not is_user_id_valid:
        response = gen_meal_plan(data)
    else:

        


    # scheduled_email_test()
    # print("email content", create_sample_email_content(response))
    # print("Response", response)
    return jsonify(response)

def _extract_user_profile_data_from_json(data):
    person = data.get('people')[0] if data.get('people') else {}
    return {
        'user_id': 100,  # Example static ID, should be dynamically set if needed
        'gender': person.get('gender'),
        'height': person.get('height'),
        'weight': person.get('weight'),
        'age': person.get('age'),
        'activity_level': person.get('activityLevel'),
        'selected_unit': data.get('selectedUnit'),
        'health_goal': data.get('healthGoal')
    }

def _extract_data_from_json(data):
    return {
        'allergies': data.get('allergies'),
        'liked_foods': data.get('likedFoods'),
        'disliked_foods': data.get('dislikedFoods'),
        'favourite_cuisines': data.get('favouriteCuisines'),
        'religious_constraint': data.get('religiousConstraint'),
        'dietary_constraint': data.get('dietaryConstraint')
    }

def _process_user_data(db, user_id, extract_data):
    db.add_user_allergies(user_id, extract_data['allergies'])
    db.add_user_liked_foods(user_id, extract_data['liked_foods'])
    db.add_user_disliked_foods(user_id, extract_data['disliked_foods'])
    db.add_user_favourite_cuisines(user_id, extract_data['favourite_cuisines'])
    db.insert_user_religious_constraint(user_id, extract_data['religious_constraint'])
    db.insert_user_dietary_constraint(user_id, extract_data['dietary_constraint'])

def _retrieve_user_data(db, user_id):
    


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

        # Get the user_id from Firebase
        # user_id = firebase_auth.current_user.uid

        return handle_checkout_session_completed(session)
        # return handle_checkout_session_completed(session, user_id)
    else:
        print('Unhandled event type {}'.format(event['type']))
        return jsonify(success=True), 200
    

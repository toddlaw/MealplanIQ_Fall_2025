from flask import redirect, request, jsonify, send_from_directory
from app import app
from app.generate_meal_plan import gen_meal_plan
from app.payment_stripe import create_subscription, cancel_subscription
from user_db.user_db import instantiate_database

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
    response = gen_meal_plan(data)
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


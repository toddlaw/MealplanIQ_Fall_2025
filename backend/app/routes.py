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


@app.route('/api', methods=['POST'])
def receive_data():
    print("Received data", request.json)
    db = instantiate_database()
    data = request.json
    user_id = 100
    user_name = "Test" 
    person = data.get('people')[0] if data.get('people') else {}
    gender = person.get('gender')
    height = person.get('height')
    weight = person.get('weight')
    age = person.get('age')
    activity_level = person.get('activityLevel')
    selected_unit = data.get('selectedUnit')
    goal = data.get('healthGoal') 
    allergies = data.get('allergies')
    liked_foods = data.get('likedFoods')
    disliked_foods = data.get('dislikedFoods')
    favourite_cuisines = data.get('favouriteCuisines')
    religious_constrains = data.get('religiousConstraint')
    dietary_constrains = data.get('dietaryConstraint')

    db.insert_user_profile(user_id, user_name, gender, height, weight, age, activity_level, selected_unit, goal)
    db.add_user_allergies(user_id, allergies)
    db.add_user_liked_foods(user_id, liked_foods)
    db.add_user_disliked_foods(user_id, disliked_foods)
    db.add_user_favourite_cuisines(user_id, favourite_cuisines)
    db.insert_user_religious_constraints(user_id, religious_constrains)
    db.insert_user_dietary_constraint(user_id, dietary_constrains)

    
    response = gen_meal_plan(data)
    return jsonify(response)



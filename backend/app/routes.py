from flask import redirect, request, jsonify, send_from_directory
from app import app
from app.generate_meal_plan import gen_meal_plan
from app.payment_stripe import create_charge
from app.payment_stripe import create_subscription

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

@app.route('/create-charge', methods=['POST'])
def handle_create_charge():
    email = request.json.get('email')
    token = request.json.get('token')
    plan_id = request.json.get('plan_id')
    # return create_charge(token, amount)
    return create_subscription(email, token, plan_id)

@app.route('/api/endpoint', methods=['POST'])
def receive_data():
    data = request.json

    response = gen_meal_plan(data)
    return jsonify(response)

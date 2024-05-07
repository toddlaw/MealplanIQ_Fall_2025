from flask import redirect, request, jsonify, send_from_directory
from app import app
from app.generate_meal_plan import gen_meal_plan
import stripe

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

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/create-charge', methods=['POST'])
def create_charge():
    try:
        token = request.json.get('token')
        amount = request.json.get('amount')

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Example charge',
            source=token
        )
        return jsonify(charge), 200
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400

@app.route('/api/endpoint', methods=['POST'])
def receive_data():
    data = request.json

    response = gen_meal_plan(data)
    return jsonify(response)

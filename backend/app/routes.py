from flask import redirect, request, jsonify, send_from_directory
from app import app
from app.generate_meal_plan import gen_meal_plan
from flask_cors import CORS


# Enable CORS for all domains on all routes
CORS(app)



# enable CORS
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

@app.route('/api/endpoint', methods=['POST'])
def receive_data():
    data = request.json

    response = gen_meal_plan(data)
    return jsonify(response)

import time

from app import app
from app.calculate_bmi import bmi_calculator_function
from flask import redirect, request, jsonify, send_from_directory
from flask_cors import CORS
from app.generate_meal_plan import gen_meal_plan, gen_shopping_list
from app.calculate_energy import energy_calculator_function
from app.calculate_nutritional_requirements import calculate_macros, calculate_micros, read_micro_nutrients_file
from app.send_email import create_and_send_maizzle_email_test
from app.payment_stripe import (
    handle_checkout_session_completed,
    handle_subscription_deleted,
    handle_subscription_updated,
    create_trial_payment_and_subscription,
    create_customer_portal_by_id
)
from app.manage_user_data import *
from user_db.user_db import instantiate_database
import stripe
from app.find_matched_recipe_and_update import find_matched_recipe_and_update, find_matched_recipe_and_delete, update_nutrition_values
from app.recipe_management.search import search_recipes_logic
from app.recipe_management.replace import replace_recipe_logic
from app.recipe_management.get_recipe import get_recipe_logic

# from app.send_email import send_weekly_email_by_google_scheduler

# Enable CORS for all domains on all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# serve static files
import traceback


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    if path:
        return send_from_directory("static", path)
    else:
        return send_from_directory("static", "index.html")


@app.route("/static/splash")
@app.route("/static/mission")
@app.route("/static/philosophy")
@app.route("/static/approach")
@app.route("/static/technology")
@app.route("/static/leadership")
@app.route("/static/timeline")
@app.route("/static/contact")
@app.route("/static/login")
@app.route("/static/sign-up")
@app.route("/static/profile")
@app.route("/static")
def static_files():
    return send_from_directory("static", "index.html")


# redirect 404 to root URL
# @app.errorhandler(404)
# def page_not_found(e):
#     print(request.path)
#     return redirect("/")
# @app.errorhandler(404)
# def page_not_found(e):
#     if request.path.startswith('/api'):
#         return jsonify({'error': 'Not found'}), 404
#     return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 Not Found errors.

    If the requested path begins with '/api', a JSON error response is returned.
    Otherwise, the user is redirected to the homepage.

    Parameters:
    -----------
    e : Exception
        The exception instance representing the 404 error.

    Returns:
    --------
    Response
        - For API requests: JSON response with error message and status code 404.
        - For non-API requests: Redirect response to the homepage ('/').
    --------
    @author: BCIT May 2025
    """
    if request.path.startswith('/api'):
        return jsonify({'error': 'Not found'}), 404
    return redirect("/")


# @app.route("/schedule-email", methods=["GET"])
# def schedule_email():
#     if request.headers.get("X-Appengine-Cron") != "true":
#         return "Unauthorized", 403
#     db = instantiate_database()
#     send_weekly_email_by_google_scheduler(db)


@app.route("/signup", methods=["POST"])
def handle_signup():
    data = request.json
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    email = data.get("email")
    stripe_subscription_id = data.get("subscription_id")
    stripe_customer_id = data.get("customer_id")
    stripe_trial_end = data.get("trial_end")
    db = instantiate_database()
    try:
        if stripe_subscription_id:
            print("trying to insert paid trial users!")
            result = db.insert_new_user_with_paid_trial(
                user_id, user_name, email, stripe_subscription_id, stripe_customer_id, stripe_trial_end
            )
        else:
            result = db.insert_user_and_set_default_subscription_signup(
                user_id, user_name, email
            )
        return result
    except Exception as e:
        print(f"Failed to insert user: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/<path:path>", methods=["OPTIONS"])
def handle_preflight(path):
    response = jsonify({"status": "preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response



@app.route("/api/profile/<user_id>")
def get_user_profile(user_id):
    db = instantiate_database()
    result = db.get_user_profile(user_id)
    return result


@app.route("/api/landing/profile/<user_id>")
def get_user_landing_page_profile(user_id):
    db = instantiate_database()
    result = db.get_user_landing_page_profile(user_id)
    return result


@app.route("/api", methods=["POST"])
def receive_data():
    data = request.json
    print("get data from frontend", data)
    db = instantiate_database()
    user_id = data["user_id"]
    user_data = extract_user_profile_data_from_json(data, user_id)
    extract_data = extract_data_from_json(data)
    # db.update_user_profile(**user_data)
    process_user_data(db, user_id, extract_data)

    try:
        print("data sent to gen_meal_plan", data)
        response = gen_meal_plan(data)
    except Exception as e:
        error_traceback = traceback.format_exc()
        response = {"error": str(e),
                    "traceback": error_traceback}
        print(f"Failed to generate meal plan: {str(e)}\nTraceback: {error_traceback}")

    try:
        create_and_send_maizzle_email_test(response, user_id, db)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    return jsonify(response)


@app.route("/api/refresh-meal-plan", methods=["POST"])
def get_meal_plan_refresh():

    data = request.json
    meal_plan_data = data.get("meal_plan")
    #print("MEAL PLAN DATA========\n\n",meal_plan_data)
    recipe_id = data.get("recipe_id")

    try:
        output_data = find_matched_recipe_and_update(meal_plan_data, recipe_id)

    except ValueError as e:
        output_data = {"error": str(e)}
        print(f"Failed to generate meal plan: {str(e)}")
    # print('OUTPUT DATA \n',output_data)
    # Return the modified template data as JSON response
    return jsonify(output_data)

@app.route("/api/delete-recipe", methods=["POST"])
def delete_recipe():
    data = request.json
    meal_plan_data = data.get("meal_plan")
    recipe_id = data.get("recipe_id")

    try:
        output_data = find_matched_recipe_and_delete(meal_plan_data, recipe_id)
    except ValueError as e:
        output_data = {"error": str(e)}
        print(f"Failed to generate meal plan: {str(e)}")

    return jsonify(output_data)

@app.route("/api/get-shopping-list", methods=["POST"])
def get_meal_plan():
    response = request.json
    response_with_shopping_list = gen_shopping_list(response)
    return jsonify(response_with_shopping_list["shopping_list"])


@app.route("/api/subscription_type_id/<user_id>")
def get_subscription_type_id(user_id):
    db = instantiate_database()
    cursor = db.db.cursor()
    query = "SELECT subscription_type_id FROM user_subscription WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        subscription_type_id = result[0]
        print(
            f"Found subscription_type_id: {subscription_type_id} for user_id: {user_id}"
        )
        return jsonify({"subscription_type_id": subscription_type_id})
    else:
        print(f"No subscription_type_id found for user_id: {user_id}")
        return jsonify({"error": "User not found"}), 404

@app.route("/api/get-bmi", methods=["POST"])
def get_bmi():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        weight = data.get("weight")
        height = data.get("height")

        if weight is None or height is None:
            return jsonify({"error": "Missing weight or height"}), 400

        bmi = bmi_calculator_function(weight, height)
        return jsonify({"bmi": bmi})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/get-nutrition-requirements", methods=["POST"])
def get_nutrition_requirements():
    try: 
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        age = data.get("age")
        bmi = data.get("bmi")
        gender = data.get("gender")
        weight = data.get("weight")
        height = data.get("height")
        activityLevel = data.get("activityLevel")

        if None in [age, bmi, gender, weight, height, activityLevel]:
            return jsonify({"error": "Missing required fields"}), 400

        energy = [energy_calculator_function(age, bmi, gender, weight, height, activityLevel)]  
        macros = calculate_macros(energy, [data])
        micros = calculate_micros([data])

        data = { "energy": energy[0], "macros": macros, "micros": micros }
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/one-day-meal-plan-api", methods=["POST"])
def create_one_day_meal_plan():
    data = request.json
    print("get data from frontend", data)

    try:
        print("data sent to gen_meal_plan", data)
        response = gen_meal_plan(data)
    except Exception as e:
        error_traceback = traceback.format_exc()
        response = {"error": str(e),
                    "traceback": error_traceback}
        print(f"Failed to generate meal plan: {str(e)}\nTraceback: {error_traceback}")
        
    # try:
    #     create_and_send_maizzle_email_test(response, user_id, db)
    # except Exception as e:
    #     print(f"Failed to send email: {str(e)}")
    return jsonify(response)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("In webhook")
    endpoint_secret = (
        "whsec_d50a558aab0b7d6b048b21ec26aaf7aceeb99959c40d60d08d5973b76d6db560"
    )
    # webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    event = None
    payload = request.data
    sig_header = request.headers.get("STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            # Use webhook_secret instead of endpoint_secret for deployment
            payload,
            sig_header,
            endpoint_secret,
        )
    except ValueError as e:
        print("ValueError: ", e)
        return jsonify(error="Invalid payload"), 400
    except stripe.error.SignatureVerificationError as e:
        print("SignatureVerificationError: ", e)
        return jsonify(error="Invalid signature"), 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        print("checkout.session.completed event received")
        return handle_checkout_session_completed(session, user_id)
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        print("customer.subscription.updated event received")
        return handle_subscription_updated(subscription)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        print("customer.subscription.deleted event received")
        return handle_subscription_deleted(subscription)
    else:
        print("Unhandled event type {}".format(event["type"]))
        return jsonify(success=True), 200


@app.route("/api/update_user_profile_from_dashboard", methods=["POST"])
def update_user_profile_from_dashboard():
    print("1000")
    data = request.json
    db = instantiate_database()
    print("dashboard data received:", data)
    user_id = data.get("user_id")
    print("expected user id", user_id)
    try:
        db.update_user_profile_from_dashboard(**data)
        return jsonify({"message": "Profile updated in database successfully from dashboard"}), 200
    except Exception as e:
        print(f"Error updating profile in database from dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/trial-payment", methods=["POST"])
def handle_payment():
    data = request.json
    try:
        result = create_trial_payment_and_subscription(data)
        return jsonify({'success': True, **result})
    except stripe.error.CardError as e:
        err = e.error
        print('Stripe Card Error:', err.message)
        return jsonify({'success': False, 'error': err.message}), 400
    except Exception as e:
        print('Server Error:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route("/create-customer-portal", methods=["POST"])
def create_customer_portal_session():
    user_id = request.json.get("uid")
    url, error = create_customer_portal_by_id(user_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"url": url})

@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    """
    Search for recipes based on a query string.

    Query Parameters:
    -----------------
    q : str
        The search query (matched against title, ingredients, region, and subregion).
    exact : str
        Whether to enforce exact term match ('true' or 'false').

    Returns:
    --------
    Response
        A JSON list of matching recipes, each containing:
        - id (int)
        - title (str)
        - calories (float)
        - region (str)
        - prep_time (str)
        - cook_time (str)
    --------
    @author: BCIT May 2025
    """
    query = request.args.get('q', '').lower().strip()
    exact_match = request.args.get('exact', 'false').lower() == 'true'
    return search_recipes_logic(query, exact_match)


@app.route("/api/replace-meal-plan-recipe", methods=["POST"])
def replace_recipe_in_meal_plan():
    """
    Replace a recipe in a given meal plan with a new recipe.

    Request Body:
    -------------
    JSON object with the following keys:
        - meal_plan (dict): The current meal plan.
        - recipe_id (dict): Contains the 'id' of the replacement recipe.
        - day_index (int): Index of the day in the meal plan.
        - recipe_index (int): Index of the recipe to replace.

    Returns:
    --------
    Response
        A JSON object containing:
        - meal_plan (dict): Updated meal plan with nutrition and shopping list updates.
        - id_replaced (int): The ID of the recipe that replaced the old one.
    --------
    @author: BCIT May 2025
    """
    data = request.json
    return replace_recipe_logic(data)


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """
    Retrieve detailed information for a specific recipe by ID.

    URL Parameters:
    ---------------
    recipe_id : int
        The unique identifier of the recipe.

    Returns:
    --------
    Response
        A JSON object containing:
        - id (int)
        - title (str)
        - calories (float)
        - region (str)
        - prep_time (str)
        - ingredients (str)
        - instructions (str)

        If the recipe is not found, returns:
        - error (str): Message indicating recipe not found
        - HTTP status code 404
    --------
    @author: BCIT May 2025
    """
    return get_recipe_logic(recipe_id)
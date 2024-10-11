from app import app
from flask import redirect, request, jsonify, send_from_directory
from flask_cors import CORS
from app.generate_meal_plan import gen_meal_plan, gen_shopping_list
from app.send_email import create_and_send_maizzle_email_test
from app.payment_stripe import (
    handle_checkout_session_completed,
    handle_subscription_deleted,
    handle_subscription_updated,
)
from app.manage_user_data import *
from user_db.user_db import instantiate_database
import stripe
from app.find_matched_recipe_and_update import find_matched_recipe_and_update
# from app.send_email import send_weekly_email_by_google_scheduler

# Enable CORS for all domains on all routes
CORS(app)

# serve static files


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
@app.errorhandler(404)
def page_not_found(e):
    print(request.path)
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
    db = instantiate_database()
    try:
        result = db.insert_user_and_set_default_subscription_signup(
            user_id, user_name, email
        )
        return result
    except Exception as e:
        print(f"Failed to insert user: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
    db = instantiate_database()
    user_id = data["user_id"]
    user_data = extract_user_profile_data_from_json(data, user_id)
    extract_data = extract_data_from_json(data)

    db.update_user_profile(**user_data)
    process_user_data(db, user_id, extract_data)

    try:
        response = gen_meal_plan(data)
    except Exception as e:
        response = {"error": str(e)}
        print(f"Failed to generate meal plan: {str(e)}")

    try:
        create_and_send_maizzle_email_test(response, user_id, db)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    return jsonify(response)


@app.route("/api/refresh-meal-plan", methods=["POST"])
def get_meal_plan_refresh():

    data = request.json
    meal_plan_data = data.get("meal_plan")
    recipe_id = data.get("recipe_id")

    try:
        output_data = find_matched_recipe_and_update(meal_plan_data, recipe_id)

    except ValueError as e:
        output_data = {"error": str(e)}
        print(f"Failed to generate meal plan: {str(e)}")

    # Return the modified template data as JSON response
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

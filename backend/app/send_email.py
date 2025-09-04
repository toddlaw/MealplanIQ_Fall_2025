import os
import base64
import datetime
from datetime import date, datetime, timedelta
from sched import scheduler
from zoneinfo import ZoneInfo
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.generate_meal_plan import (
    gen_meal_plan,
    process_type_normal,
)
from app.mealplan_service import download_mealplan_json_from_gcs, upload_mealplan_json_to_gcs
from app.manage_user_data import create_data_input_for_auto_gen_meal_plan

from email.mime.text import MIMEText
from flask import Flask, jsonify, render_template, render_template_string
import subprocess
import json
import time
from app.shopping_list_utils import (
    transform_meal_plan_to_shopping_list,
    process_and_categorize_shopping_list
)

from user_db.user_db import instantiate_database
from app.moc.sampleMealPlans import data as sampleMealPlans
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)

SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_JSON')
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

credentials = service_account.Credentials.from_service_account_info(
  SERVICE_ACCOUNT_INFO,
  scopes=['https://www.googleapis.com/auth/gmail.send'],
  subject=os.getenv('SENDER_EMAIL')
)

service_gmail = build("gmail", "v1", credentials=credentials)

TZ = ZoneInfo("America/Los_Angeles")  

now = datetime.now(TZ)        
today = now.date()           
start_date = today + timedelta(days=1)  
end_date   = start_date + timedelta(days=6) 

today_str = today.strftime("%Y-%m-%d")
start_str = start_date.strftime("%Y-%m-%d")
end_str   = end_date.strftime("%Y-%m-%d")

# today = datetime.today()
# start_date = today + timedelta(days=1)
# end_date = start_date + timedelta(days=6)
# today_str = today.strftime('%Y-%m-%d')
# start_str = start_date.strftime('%Y-%m-%d')
# end_str = end_date.strftime('%Y-%m-%d')

# add is_html parameter to create_message function with html content
def create_message(sender, to, subject, message_text, is_html=True):
    subtype = "html" if is_html else "plain"
    message = MIMEText(message_text, subtype)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {"raw": raw_message.decode("utf-8")}

def send_message(service, user_id, message):
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print("Message Id: %s" % message["id"])
        return message
    except Exception as e:
        print("An error occurred: %s" % e)
        return None
    
# multi-threading test code
# def send_email_by_google_scheduler(db, is_daily=False):
#     user_ids = db.get_all_subscribed_users()  

#     def job(user_id):
#         if is_daily:
#             process_daily_email_for_user(user_id)
#         else:
#             process_weekly_email_for_user(user_id, db)

#     with ThreadPoolExecutor(max_workers=5) as executor:
#         executor.map(job, user_ids)

def send_email_by_google_scheduler(db, is_daily=False):
    user_ids = db.get_all_subscribed_users()  
    
    if not user_ids:
        result = {
            "status": "skip",
            "reason": "no subscribed users exist",
        }
        return result, 200
    
    success_results = []
    failed_results = []
    
    for user_id in user_ids:
        if is_daily:
            result, code = process_daily_email_for_user(db, user_id)
        else:
            result, code = process_weekly_email_for_user(db, user_id)
            
        if result.get("status") == 'success':
            success_results.append({
                "code": code,
                "result": result
            })
        else:
            failed_results.append({
                "code": code,
                "result": result
            })
            
    final_status = "partial_fail" if failed_results else "success"
    return {
        "status": final_status,
        "total_users": len(user_ids),
        "success_count": len(success_results),
        "fail_count": len(failed_results),
        "succes": success_results,
        "fail": failed_results
    }, 207 if failed_results else 200

def process_weekly_email_for_user(db, user_id):
    try:
        data = create_data_input_for_auto_gen_meal_plan(db, user_id, start_date, end_date)
        response = gen_meal_plan(data)
        db.insert_user_meal_plan(user_id, response, start_date, end_date)
        
        path = f"meal-plans-for-user/{user_id}/{start_str}_to_{end_str}.json"
        upload_mealplan_json_to_gcs(response, path)
        
        user_name = db.retrieve_user_name(user_id)
        user_email = db.retrieve_user_email(user_id)
        gmail_response = create_and_send_maizzle_email(response, user_email, user_name, start_str, end_str)
        return {
            "status": "success",
            "user_id": user_id,
            "user_email": user_email,
            "gmail_response": gmail_response,
            "start_date": start_str,
            "end_date": end_str
        }, 200
    except Exception as e:
        return {
            "status": "fail",
            "user_id": user_id,
            "error": str(e)
        }, 500

def process_daily_email_for_user(db, user_id):
    tomorrow_str = start_date.strftime('%Y-%m-%d')

    # Get meal plan data from GCS
    try:
        full_path = f"meal-plans-for-user/{user_id}/{start_str}_to_{end_str}.json"
        data = download_mealplan_json_from_gcs(full_path)
    except Exception as e:
        return {
            "status": "fail",
            "stage": "fetch",
            "user_id": user_id,
            "date": today_str,
            "error": str(e),
        }, 500
    
    # Send daily email
    try:
        matched_day = None
        for day in data.get("days", []):
            if day.get("date") == tomorrow_str:
                matched_day = day
                break
            
        if not matched_day:
            return {
                "status": "fail",
                "stage": "filter",
                "user_id": user_id,
                "date": today_str,
                "error": f"No meal plan found for {tomorrow_str}",
            }, 404

        user_name = db.retrieve_user_name(user_id)
        user_email = db.retrieve_user_email(user_id)
        gmail_response = create_and_send_maizzle_daily_email_test({"days": [matched_day]}, user_email, user_name, tomorrow_str)

        return {
            "status": "success",
            "user_id": user_id,
            "user_email": user_email,
            "date": tomorrow_str,
            "gmail_response": gmail_response
        }, 200

    except Exception as e:
        return {
            "status": "fail",
            "stage": "send",
            "user_id": user_id,
            "date": tomorrow_str,
            "error": str(e),
        }, 500
# weekly
def create_and_send_maizzle_email(response, user_email, user_name, start_date=None, end_date=None):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = user_email
    root_path = app.root_path

    start_d = date.fromisoformat(start_date)  
    end_d = date.fromisoformat(end_date)

    templates_path = os.path.join(root_path, "emailTemplates")
    # if start_date == end_date:
    #     subject = f"Your personalized Meal Plan For tomorrow {start_d.weekday()} is Ready, {user_name}!"
    subject = f"Your personalized Meal Plan For tomorrow {start_d.weekday()} is Ready, {user_name}!"
    # else:
    #     # subject = f"Your weekly meal plan for {start_d.strftime('%b %d')} to {end_d.strftime('%b %d')}, {user_name}!"
    #     subject = "Next week’s meal plan is ready!"

    # subject = f"Your personalized Meal Plan is Ready, {user_name}!"
    response = sampleMealPlans
    response["user_name"] = user_name
    
    # Transform & aggregate raw shopping list data
    raw_list = transform_meal_plan_to_shopping_list(response)
    ordered_categories, categorized_map = process_and_categorize_shopping_list(raw_list)

    with app.app_context():
        shopping_list_template = render_template_string(
            open(templates_path + "/shoppingList.html").read(), 
            ordered_categories=ordered_categories,
            categorized_map=categorized_map
        )
        
        email_template = render_template_string(
            open(templates_path + "/weekly.html").read(), 
            **response,
            start_date=start_date,
            end_date=end_date,
            shopping_list_html=shopping_list_template,
        )

        message = create_message(
            sender_email, to_email, subject, email_template, True
        )
        msg = send_message(service_gmail, "me", message)
        print(msg)
    return msg
#daily
def create_and_send_maizzle_daily_email_test(response, user_email, user_name, sent_date):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = user_email
    
    root_path = app.root_path

    templates_path = os.path.join(root_path, "emailTemplates")
    start_d = date.fromisoformat(sent_date)

    # subject for daily email
    subject = f"Your personalized Meal Plan For tomorrow {start_d.strftime('%A')  } is Ready, {user_name}!"
    
    response["user_name"] = user_name
    
    # Transform & aggregate raw shopping list data
    raw_list = transform_meal_plan_to_shopping_list(response)
    ordered_categories, categorized_map = process_and_categorize_shopping_list(raw_list)

    with app.app_context():
        shopping_list_template = render_template_string(
            open(templates_path + "/shoppingList.html").read(), 
            ordered_categories=ordered_categories,
            categorized_map=categorized_map
        )
        
        email_template = render_template_string(
            open(templates_path + "/daily.html").read(), 
            **response,
            sent_date=sent_date,
            formatted_date=start_d.strftime('%A'),
            shopping_list_html=shopping_list_template
        )

        message = create_message(
            sender_email, to_email, subject, email_template, True
        )
        msg = send_message(service_gmail, "me", message)
        print(msg)

    return msg
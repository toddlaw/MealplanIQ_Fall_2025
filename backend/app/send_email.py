import os
import base64
import datetime
from datetime import datetime, timedelta
from sched import scheduler
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
from app.mealplan_service import upload_mealplan_json_to_gcs
from app.manage_user_data import create_data_input_for_auto_gen_meal_plan

from email.mime.text import MIMEText
from flask import Flask, render_template, render_template_string
import subprocess
import json
import time
from app.shopping_list_utils import (
    transform_meal_plan_to_shopping_list,
    process_and_categorize_shopping_list
)

from user_db.user_db import instantiate_database
from app.moc.sampleMealPlans import data as sampleMealPlans

app = Flask(__name__)

SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_JSON')
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

credentials = service_account.Credentials.from_service_account_info(
  SERVICE_ACCOUNT_INFO,
  scopes=['https://www.googleapis.com/auth/gmail.send'],
  subject=os.getenv('SENDER_EMAIL')
)

service_gmail = build("gmail", "v1", credentials=credentials)


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


def send_weekly_email_by_google_scheduler(db):
    today = datetime.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=6)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # user_ids = db.get_all_subscribed_users()
    # for user_id in user_ids:
    user_id = "59JNe2o0WGdwxfmQrbGN4pbF4jk2"
    try:
        data = create_data_input_for_auto_gen_meal_plan(db, user_id, start_date, end_date)
        response = gen_meal_plan(data)
        print(f"User meal plan generated: {user_id}")
        db.insert_user_meal_plan(user_id, response, start_date, end_date)
        
        path = f"meal-plans-for-user/{user_id}/{start_str}_to_{end_str}.json"
        upload_mealplan_json_to_gcs(response, path)
        
        user_name = db.retrieve_user_name(user_id)
        user_email = db.retrieve_user_email(user_id)
        create_and_send_maizzle_weekly_email_test(response, user_email, user_name, start_str, end_str)
        print(f"Email has sent successfully: {user_id}")
    except Exception as e:
        print(f"ERROR!! Failed to process user {user_id}: {e}")

def send_daily_email_by_google_scheduler(db):
    today = datetime.today()
    start_str = today.strftime('%Y-%m-%d')




def create_and_send_maizzle_weekly_email_test(response, user_email, user_name="Julie", start_date=None, end_date=None):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = user_email
    root_path = app.root_path

    templates_path = os.path.join(root_path, "emailTemplates")
    subject = f"Your personalized Meal Plan is Ready, {user_name}!"
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
            start_date=start_date,
            end_date=end_date,
            shopping_list_html=shopping_list_template,
            **response
        )

        message = create_message(
            sender_email, to_email, subject, email_template, True
        )
        msg = send_message(service_gmail, "me", message)
        print(msg)


def create_and_send_maizzle_daily_email_test(response, user_name, sent_date):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = "ohjeoung5224@gmail.com"

    root_path = app.root_path

    templates_path = os.path.join(root_path, "emailTemplates")
    subject = f"Your personalized Meal Plan is Ready, {user_name}!"
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
            shopping_list_html=shopping_list_template
        )

        message = create_message(
            sender_email, to_email, subject, email_template, True
        )
        msg = send_message(service_gmail, "me", message)
        print(msg)

import os
import base64
import datetime
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
from app.manage_user_data import create_data_input_for_auto_gen_meal_plan
from email.mime.text import MIMEText
from flask import Flask, render_template_string
import subprocess
import json
import time

from user_db.user_db import instantiate_database

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
    today = datetime.datetime.today().strftime("%A")
    user_ids_emails = db.retrieve_user_id_and_emails_by_last_meal_plan_date(today)
    for user_id, email in user_ids_emails:
        create_and_send_maizzle_email_test(db, user_id)


def create_and_send_maizzle_email_test(response, user_id, db):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = "ekska21@gmail.com"
    user_name = db.retrieve_user_name(user_id)

    root_path = app.root_path

    templates_path = os.path.join(root_path, "emailTemplates")
    subject = f"Your personalized Meal Plan is Ready, {user_name}!"
    response["user_name"] = user_name

    with app.app_context():
        email_template = render_template_string(
            open(templates_path + "/content.html").read(), **response
        )

        message = create_message(
            sender_email, to_email, subject, email_template, True
        )
        msg = send_message(service_gmail, "me", message)
        print(msg)

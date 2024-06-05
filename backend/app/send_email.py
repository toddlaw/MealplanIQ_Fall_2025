import os
import base64
import datetime
from sched import scheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.generate_meal_plan import (
    distribute_snacks_to_date,
    gen_meal_plan,
    insert_snacks_between_meals,
    process_response_meal_name,
    process_type_normal,
)
from app.manage_user_data import create_data_input_for_auto_gen_meal_plan
from email.mime.text import MIMEText
from flask import Flask, render_template_string
import subprocess
import json
import time
import pdfkit

from user_db.user_db import instantiate_database

app = Flask(__name__)

# import scheduler
# from flask_apscheduler import APScheduler

dir_path = os.path.dirname(os.path.realpath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(dir_path, "service-key.json")

credentials = service_account.Credentials.from_service_account_file(
    filename=SERVICE_ACCOUNT_FILE,
    scopes=["https://mail.google.com/"],
    subject=os.getenv("SENDER_EMAIL"),
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


def create_message_with_attachment(
    sender_email, to_email, subject, message_text, attachment
):
    message = MIMEMultipart()
    message["to"] = to_email
    message["from"] = sender_email
    message["subject"] = subject

    msg = MIMEText(message_text, "html")
    message.attach(msg)

    part = MIMEApplication(attachment, Name="ShoppingList.pdf")
    part["Content-Disposition"] = 'attachment; filename="ShoppingList.pdf"'
    message.attach(part)

    # Encode the bytes for sending via Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


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
        create_and_send_maizzle_email(db, user_id)


def email_by_generation_button(request_data, db):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    receiver_email = db.retrieve_user_email(request_data["user_id"])
    subject = "Test Email"
    message_text = create_sample_email_content(request_data)
    message = create_message(sender_email, receiver_email, subject, message_text)
    try:
        send_message(service_gmail, "me", message)
        print(f"Email sent to {receiver_email} with subject {subject}.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    else:
        user_id = request_data["user_id"]
        db.update_user_last_date_plan_profile(user_id, request_data["maxDate"])


def scheduled_email(db, user_id):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    receiver_email = db.retrieve_user_email(user_id)
    subject = "Meal Plan for the Week"
    request_data = create_data_input_for_auto_gen_meal_plan(db, user_id)
    message_text = create_sample_email_content(request_data)
    message = create_message(sender_email, receiver_email, subject, message_text)
    try:
        send_message(service_gmail, "me", message)
        print(f"Email sent to {receiver_email} with subject {subject}.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    else:
        db.update_user_last_date_plan_profile(user_id, request_data["maxDate"])


def scheduled_email_test_clicked_by_generation_button(request_data, db):
    initial_run_time = datetime.datetime.now()

    job_id = f"email_job_{(initial_run_time).strftime('%Y%m%d%H%M%S')}"
    try:
        scheduler.add_job(
            func=email_by_generation_button,
            id=job_id,
            args=[request_data, db],
            trigger="date",
            run_date=initial_run_time,
        )
        print(f"Email scheduled to send at {initial_run_time} with job ID {job_id}.")
    except Exception as e:
        print(f"Failed to schedule email for week: {str(e)}")
    return initial_run_time


def scheduled_email_test(email_sent_time, db, user_id):
    initial_run_time = email_sent_time + datetime.timedelta(minutes=2)
    num_of_emails_to_be_sent = 2

    for i in range(num_of_emails_to_be_sent):
        run_time = initial_run_time + datetime.timedelta(minutes=2 * i)
        job_id = f"email_job_{(run_time + datetime.timedelta(weeks=i)).strftime('%Y%m%d%H%M%S')}"
        try:
            scheduler.add_job(
                func=scheduled_email,
                id=job_id,
                args=[db, user_id],
                trigger="date",
                run_date=run_time,
            )
            print(f"Email scheduled to send at {run_time} with job ID {job_id}.")
        except Exception as e:
            print(f"Failed to schedule email for week {i+1}: {str(e)}")


def create_sample_email_content(request_data):
    response = gen_meal_plan(request_data)
    days = response["days"]
    email_content = ""
    email_content += f"Meal Plan\n"
    for day in days:
        email_content += f"Date: {day['date']}\n"
        for recipe in day["recipes"]:
            email_content += f"title: {recipe['title']}, id: {recipe['id']}\n"
        email_content += "\n"
    return email_content


def create_and_send_maizzle_email(db, user_id, request_data=None):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = db.retrieve_user_email(user_id)

    root_path = app.root_path
    json_file_path = os.path.join(root_path, "maizzleTemplates", "output.json")

    if request_data is None:
        request_data = create_data_input_for_auto_gen_meal_plan(db, user_id)
    message_text = gen_meal_plan(request_data)
    db.update_user_last_date_plan_profile(user_id, request_data["maxDate"])

    # Write the template data to the JSON file
    # with open(json_file_path, "w+") as f:
    #     json.dump(message_text, f)
    #     f.flush()  # Ensure all data is written to the disk
    #     os.fsync(
    #         f.fileno()
    #     )  # Ensure all internal buffers associated with f are written to disk

    maizzle_project_path = os.path.join(root_path, "maizzleTemplates")
    subject = "Text Email"
    message_text = "text email with image?!!"

    # Run the Maizzle build command
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=maizzle_project_path,
            capture_output=True,
            text=True,
            # shell=True,  # Add shell=True to ensure the command runs correctly on Windows
            encoding="utf-8",
        )
        if result.returncode == 0:
            time.sleep(15)
            with app.app_context():
                email_template = render_template_string(
                    open(maizzle_project_path + "/build_production/index.html").read()
                    # window path
                    # open(maizzle_project_path + "\\build_production\\index.html").read()
                )

                shopping_list_template = render_template_string(
                    open(
                        maizzle_project_path + "/build_production/shoppingList.html"
                    ).read()
                    # window path
                    # open(
                    #     maizzle_project_path + "\\build_production\\shoppingList.html"
                    # ).read()
                )

            # Convert the rendered HTML to PDF
            shopping_list_pdf = pdfkit.from_string(
                shopping_list_template, False, options={"enable-local-file-access": ""}
            )

            message = create_message_with_attachment(
                sender_email, to_email, subject, email_template, shopping_list_pdf
            )
            send_message(service_gmail, "me", message)
        else:
            print("Build failed with return code:", result.returncode)
            return "build failed"
    except Exception as e:
        print("error occur" + str(e))
        return "error occur" + str(e)


def create_and_send_maizzle_email_test(response, user_id, db):
    sender_email = "MealPlanIQ <{}>".format(os.getenv("SENDER_EMAIL"))
    to_email = db.retrieve_user_email(user_id)
    user_name = db.retrieve_user_name(user_id)

    root_path = app.root_path

    templates_path = os.path.join(root_path, "emailTemplates")
    subject = f"Your personalized Meal Plan is Ready, {user_name}!"
    response["user_name"] = user_name

    with app.app_context():
        email_template = render_template_string(
            open(templates_path + "/content.html").read(), **response
        )

        shopping_list_template = render_template_string(
            open(templates_path + "/shoppingList.html").read(), **response
        )

        shopping_list_pdf = pdfkit.from_string(
            shopping_list_template, False, options={"enable-local-file-access": ""}
        )

        message = create_message_with_attachment(
            sender_email, to_email, subject, email_template, shopping_list_pdf
        )
        send_message(service_gmail, "me", message)


def main():
    sender_email = "warren@mealplaniq.com"
    sender_email = "globalyy2020@gmail.com"
    sender_email = "ohjeoung5224@gmail.com"
    to_email = "globalyy2020@gmail.com"

    root_path = app.root_path

    json_file_path = os.path.join(root_path, "maizzleTemplates", "output.json")

    # db = instantiate_database()
    # user_id = 300
    # request_data = create_data_input_for_auto_gen_meal_plan(db, user_id)
    # message_text = gen_meal_plan(request_data)
    # db.update_user_last_date_plan_profile(user_id, request_data["maxDate"])

    # Write the template data to the JSON file
    # with open(json_file_path, "w+") as f:
    #     json.dump(message_text, f)
    #     f.flush()  # Ensure all data is written to the disk
    #     os.fsync(
    #         f.fileno()
    #     )  # Ensure all internal buffers associated with f are written to disk

    maizzle_project_path = os.path.join(root_path, "maizzleTemplates")
    # maizzle_project_path = '/Users/jeongeun/Desktop/BCIT CST/Summer_2024/MealPlanIQ_May_2024/backend/app/maizzleTemplates'
    # print(maizzle_project_path)

    subject = "Text Email"
    message_text = "text email with image?!!"

    # Run the Maizzle build command
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=maizzle_project_path,
            capture_output=True,
            text=True,
            shell=True,  # Add shell=True to ensure the command runs correctly on Windows
            encoding="utf-8",
        )
        if result.returncode == 0:
            time.sleep(15)
            with app.app_context():
                email_template = render_template_string(
                    open(maizzle_project_path + "/build_production/index.html").read()
                    # open(maizzle_project_path + "\\build_production\\index.html").read()
                    # **template_data,
                )

                shopping_list_template = render_template_string(
                    open(
                        maizzle_project_path + "/build_production/shoppingList.html"
                    ).read()
                    # open(
                    #     maizzle_project_path + "\\build_production\\shoppingList.html"
                    # ).read()
                    # **template_data,
                )

            # message = create_message_with_attachment(
            #     sender_email, to_email, subject, email_template, is_html=True
            # )

            # Convert the rendered HTML to PDF
            shopping_list_pdf = pdfkit.from_string(
                shopping_list_template, False, options={"enable-local-file-access": ""}
            )

            message = create_message_with_attachment(
                sender_email, to_email, subject, email_template, shopping_list_pdf
            )
            send_message(service_gmail, "me", message)
        else:
            print("Build failed with return code:", result.returncode)
            return "build failed"
    except Exception as e:
        print("error occur" + str(e))
        return "error occur" + str(e)


if __name__ == "__main__":
    main()

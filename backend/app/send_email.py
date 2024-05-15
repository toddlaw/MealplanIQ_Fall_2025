# pip3 install --upgrade google-auth
# pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# pip install Flask-APScheduler
# pip3 install datetime

import datetime
from sched import scheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import os
from email.mime.application import MIMEApplication

from app.generate_meal_plan import gen_meal_plan
from app.manage_user_data import create_data_input_for_auto_gen_meal_plan
from . import app, scheduler
from flask_apscheduler import APScheduler


SERVICE_ACCOUNT_FILE = 'service-key.json path'
credentials = service_account.Credentials.from_service_account_file(
  filename=SERVICE_ACCOUNT_FILE,
  scopes=['https://mail.google.com/'],
  subject='Warren email here'
)

service_gmail = build('gmail', 'v1', credentials=credentials)

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }

def create_message_with_attachment(sender_email, receiver_email, subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = receiver_email
    message['from'] = "MealPlanIQ <{}>".format(sender_email)
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    with open(file_path, 'rb') as file:
      attachment = MIMEApplication(file.read(), _subtype="pdf")
      attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
      message.attach(attachment)

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    body = {'raw': raw_message}
    return body

def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None
  
def scheduled_email_by_generation_button(request_data, db):
    sender_email = 'Warren email here'
    receiver_email = 'receiver email here'
    subject = 'Test Email'
    message_text = create_sample_email_content(request_data)
    message = create_message(sender_email, receiver_email, subject, message_text)
    try:
        send_message(service_gmail, 'me', message)
        print(f"Email sent to {receiver_email} with subject {subject}.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    else:
        user_id = request_data['user_id']
        db.update_user_last_date_plan_profile(user_id, request_data['maxDate'])
  
def scheduled_email(db, hard_coded_user_id):
    sender_email = 'Warren email here'
    receiver_email = 'receiver email here'
    subject = 'Meal Plan for the Week'
    request_data = create_data_input_for_auto_gen_meal_plan(db, hard_coded_user_id)
    message_text = create_sample_email_content(request_data)
    message = create_message(sender_email, receiver_email, subject, message_text)
    try:
        send_message(service_gmail, 'me', message)
        print(f"Email sent to {receiver_email} with subject {subject}.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    else:
        db.update_user_last_date_plan_profile(hard_coded_user_id, request_data['maxDate'])

def scheduled_email_test_clicked_by_generation_button(request_data, db, hard_coded_user_id):
    initial_run_time = datetime.datetime.now()
 
    job_id = f"email_job_{(initial_run_time).strftime('%Y%m%d%H%M%S')}"
    try:
        scheduler.add_job(func=scheduled_email_by_generation_button, 
                          id=job_id,
                          args=[request_data, db],
                          trigger='date', 
                          run_date=initial_run_time)
        print(f"Email scheduled to send at {initial_run_time} with job ID {job_id}.")
    except Exception as e:
        print(f"Failed to schedule email for week: {str(e)}")
    return initial_run_time

def scheduled_email_test(email_sent_time, db, hard_coded_user_id):
    initial_run_time = email_sent_time + datetime.timedelta(minutes=2)
    num_of_emails_to_be_sent = 2

    for i in range(num_of_emails_to_be_sent):
        run_time = initial_run_time + datetime.timedelta(minutes=2 * i)
        job_id = f"email_job_{(run_time + datetime.timedelta(weeks=i)).strftime('%Y%m%d%H%M%S')}"
        try:
            scheduler.add_job(func=scheduled_email, 
                              id=job_id,
                              args=[db, hard_coded_user_id],
                              trigger='date', 
                              run_date=run_time)
            print(f"Email scheduled to send at {run_time} with job ID {job_id}.")
        except Exception as e:
            print(f"Failed to schedule email for week {i+1}: {str(e)}")

def create_sample_email_content(request_data):
    response = gen_meal_plan(request_data)
    days = response['days']
    email_content = ""
    email_content += f"Meal Plan"
    for day in days:
        email_content += f"Date: {day['date']}\n"
        for recipe in day['recipes']:
            email_content += f"title: {recipe['title']}, id: {recipe['id']}\n"
        email_content += "\n"
    return email_content



# def main():
#   sender_email = 'warren@mealplaniq.com'
#   to_email = 'ohjeoung5224@gamil.com'
#   subject = 'Text Email'
#   message_text = 'text email with image?!!'
#   # file_path = '/Users/jeongeun/Desktop/BCIT CST/Summer_2024/MealPlanIQ_May_2024/backend/app/Activity02-Julie.pdf'
#   message = create_message(sender_email, to_email, subject, message_text)
#   # message = create_message_with_attachment(sender_email, to_email, subject, message_text, file_path)
#   # send_message(service_gmail, 'me', message)
#   scheduled_email_test(sender_email, to_email, subject, message_text)

# if __name__ == "__main__":
#     main()
#     # app.run(debug=True)

    
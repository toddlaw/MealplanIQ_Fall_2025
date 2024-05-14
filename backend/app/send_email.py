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
from . import app, scheduler
from flask_apscheduler import APScheduler


SERVICE_ACCOUNT_FILE = '/Users/jeongeun/Desktop/BCIT CST/Summer_2024/MealPlanIQ_May_2024/backend/app/service-key.json'
credentials = service_account.Credentials.from_service_account_file(
  filename=SERVICE_ACCOUNT_FILE,
  scopes=['https://mail.google.com/'],
  subject='워렌이메일'
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
  
def scheduled_email(sender_email, receiver_email, subject, message_text):
    # sender_email = 'your-email@domain.com'
    # receiver_email = 'receiver-email@example.com'
    # subject = 'Test Email'
    # message_text = 'This is a test email sent by Flask scheduler!'
    message = create_message(sender_email, receiver_email, subject, message_text)
    send_message(service_gmail, 'me', message)

def scheduled_email_test(sender_email, receiver_email, subject, message_text):
    run_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
    try:
        job_id = "email_job_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        scheduler.add_job(func=scheduled_email, id=job_id, args=[sender_email, receiver_email, subject, message_text], trigger='date', run_date=run_time)
        print(f"Email scheduled to send at {run_time} with job ID {job_id}.")
    except Exception as e:
        print(f"Failed to schedule email: {str(e)}")


def main():
  sender_email = '워렌이메일'
  to_email = '받는사람'
  subject = 'Text Email'
  message_text = 'text email with image?!!'
  # file_path = '/Users/jeongeun/Desktop/BCIT CST/Summer_2024/MealPlanIQ_May_2024/backend/app/Activity02-Julie.pdf'
  message = create_message(sender_email, to_email, subject, message_text)
  # message = create_message_with_attachment(sender_email, to_email, subject, message_text, file_path)
  # send_message(service_gmail, 'me', message)
  scheduled_email_test(sender_email, to_email, subject, message_text)

if __name__ == "__main__":
    main()
    # app.run(debug=True)

    
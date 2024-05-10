# pip3 install --upgrade google-auth
# pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import os

SERVICE_ACCOUNT_FILE = 'json파일경로'
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

def create_message_with_image(sender, to, subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    with open(file_path, 'rb') as file:
      img = MIMEImage(file.read())
      img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
      message.attach(img)

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

def main():
  sender_email = '워렌이멜'
  to_email = '받는사람이멜'
  subject = 'Text Email'
  message_text = 'text email with image?!!'
  file_path = '이미지'
  # message = create_message(sender_email, to_email, subject, message_text)
  message = create_message_with_image(sender_email, to_email, subject, message_text, file_path)
  send_message(service_gmail, 'me', message)

if __name__ == "__main__":
    main()
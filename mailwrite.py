#to send messages
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from mimetypes import guess_type as guess_mime_type
from tkinter import filedialog


SCOPES = ['https://mail.google.com/']
our_email = 'karan21258@iiitd.ac.in'

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()

def add_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(filename, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

def build_message(destination, obj, body, attachments=[]):
        if not attachments: # no attachments given
            message = MIMEText(body)
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = obj
        else:
            message = MIMEMultipart()
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = obj
            message.attach(MIMEText(body))
            for filename in attachments:
                add_attachment(message, filename)
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message():
    t=filedialog.askopenfilename(initialdir="/", title="Select message file",filetypes=(("txt files", "*.txt"),))
    with open(t,"r") as f:
        body=f.read()
    attachments = filedialog.askopenfilenames(initialdir="/", title="Select attachment",filetypes=(("txt files", "*.txt"),("all files", "*.*")))
    obj=input("enter subject: ")
    destination=input("enter destination email: ")
    return service.users().messages().send(userId="me",body=build_message(destination, obj, body, attachments)).execute()
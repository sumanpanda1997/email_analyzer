from __future__ import print_function

import os.path
import os
import shutil

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from bs4 import BeautifulSoup

import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def create_output_dir():
    if os.path.exists("email"):
        shutil.rmtree('email')
    os.makedirs("email")
    os.chdir("email")


def text_cleaning(text):
    # some text cleaning before splitting

    #removing tag patterns and whatever comes inside it 
    text = re.sub('<?/?https?:\s?/?/?\S+|</?\w>', '', text)
    text = re.sub("<.*>|\[|\]","", text)
    # remove all non ascii character
    text = re.sub(r'[^\x00-\x7F]+','', text)
    # text = re.sub(r"\r\n|\n", "", text)
    return text


def writeToFile(file_path, subject, sender, date, body):
    with open(file_path, "w", newline='') as file:
        file.write(subject+"\n")
        file.write(sender+"\n")
        file.write(date+"\n")
        body_lines = text_cleaning(body)
        file.writelines(body_lines)
        # file.writelines(body)


def parse_message(http_req_obj):
    # https://developers.google.com/resources/api-libraries/documentation/gmail/v1/python/latest/gmail_v1.users.messages.html
    subject = ""
    sender = ""
    body = ""
    date = ""
    try:
        date = http_req_obj["internalDate"]
        payload = http_req_obj["payload"]
        headers = payload["headers"]

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == "Subject":
                subject = subject+d["value"]
            if d['name'] == "From":
                sender = sender+d["value"]

        # getting the parts of body
        parts = payload.get("parts")[0]
        data = parts["body"]["data"]
        # try with body directly here
        # body = payload.get("body")
        # data = body.get("data")

        # decrypting the base64 encoding
        data = data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)

        #lxml parsing using beautifulSoup library
        soup = BeautifulSoup(decoded_data , "lxml")
        body = body+str(soup.body())        
    except:
        pass
    return subject, sender, date, body


def get_message(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        return message
    except:
        print("skipped messasage id", msg_id)
        return None

def save_messge_list(service, message_ids):
    create_output_dir()
    for idx, message_id in enumerate(message_ids):
        raw_message = get_message(service, message_id)
        if raw_message is None:
            continue
        # print(raw_message)      
        subject, sender, date, body = parse_message(raw_message)
        if subject=="" or sender=="" or date=="" or body=="":
            print("some problem with idx -> ", idx, "\n")
            print("sub -> " + subject +"\n"+"sender ->" + sender +"\n"
                +"date ->" + date + "\n" + "body_content_length ->"+str(len(body)) +"\n\n")
            continue
        writeToFile(str(idx)+"_mail.txt", subject, sender, date, body)


def get_message_ids(service, message_label, duration_in_day):
    query_time = "newer_than:" + str(duration_in_day) +"d"
    print(message_label, "\n", duration_in_day,"\n")
    try:
        messageObj = service.users().messages().list(
                userId='me', 
                labelIds=[message_label], 
                q=query_time
                ).execute()
        meta_messages = messageObj.get("messages")
        message_ids = list(map(lambda x:x["id"], meta_messages))
        return message_ids
    except:
        print("unable to retrieve message ids")
        return None

def establish_connection():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())            
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        print("unable to establish_connection please retry")
        return None



def driver(label, duration_in_day):

    service = establish_connection()
    if service is None:
        return 0

    message_ids = get_message_ids(service, label, duration_in_day)
    if message_ids is None:
        return 0

    save_messge_list(service, message_ids)
    os.chdir("../")
    print("saved successfull")


# if __name__ == '__main__':
#     main()

import requests
import json
import datetime
import time
import pandas as pd
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os

load_dotenv()  # load the values from the .env file into the environment variables



print(type(os.getenv("AUTH_ENDPOINT")))

auth_endpoint =os.getenv("AUTH_ENDPOINT")

data = {
    "email": os.getenv("EMAIL"),
    "password": os.getenv("PASSWORD"),
    "returnSecureToken": True
}
response = requests.post(auth_endpoint, data=json.dumps(data))

cred_data={
  "type": "service_account",
  "project_id": "pfe-smart-home",
  "private_key_id": f'{os.getenv("PRIVATE_ID_KEY")}',
  "private_key":f'{os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")}',
  "client_email": f'{os.getenv("CLIENT_EMAIL")}',
  "client_id": f'{os.getenv("CLIENT_ID")}',
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": f'{os.getenv("CLIENT_CERT_URL")}'
}

# Use a service account to access Firebase services
cred = credentials.Certificate(cred_data)
firebase_admin.initialize_app(cred,{
    'databaseURL': os.getenv('DATA_URL')
})

user_id=""
# Sign in the user with an email and password
if response.status_code == 200:
    user = response.json()
    user_id= user['localId']
    print('Signed in as:', user['localId'])
else:
    print('Error signing in:', response.json()['error']['message'])

ref = db.reference(f"users/{user_id}/news")
ref2 =  db.reference(f"users/{user_id}/collected")
ref2.set(False)
def collect(linkNewsPapper, name, titleP, subTP, href, root):
    now = datetime.now()
    month_day_year = now.strftime("%m%d%Y")
    
    website = linkNewsPapper
    response = requests.get(website)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    countainers = soup.select(root)
    
    titles = []
    subTitles = []
    links = []

    print(countainers)
    for e in countainers:
        
        try:
            title = e.select_one(titleP).text
            subTitle = e.select_one(subTP).text
            link = e.select_one(href)['href']
        except:
            print("error")
        
        titles.append(title)
        subTitles.append(subTitle)
        links.append(linkNewsPapper+link)
    
    data = {
        f'{name}': {
            'title': titles,
            'sub': subTitles,
            'links': links
        } 
    } 
    ref.update(data)

#collect("https://www.assabahnews.tn/","saba7",'.item-title a','.introtext','.item-title a','div.item-inner')
#collect("https://www.alchourouk.com/", "chorok", 'div div span a', 'div div div', 'div div span a', 'div.row-article.views-row')
print('script on the cloud !!')

def job():
    print("start collecting data !!")
    collect("https://www.assabahnews.tn/","saba7",'.item-title a','.introtext','.item-title a','div.item-inner')
    collect("https://www.alchourouk.com/", "chorok", 'div div span a', 'div div div', 'div div span a', 'div.row-article.views-row')
    print("*************************** data sended *****************************")
    

while True :
    current_time = datetime.datetime.now().time()
    print(f"it's : {current_time} !")
    if current_time.hour == 8 and current_time.minute == 0:
        job()
    print("wait for 45 secs")
    time.sleep(45)



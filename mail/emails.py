import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = "https://send.api.mailtrap.io/api/send"

payload = {
    "to": [
        {
            "email": "kmashao@student.wethinkcode.co.za",
            "name": "Karabo Mashao"
        }
    ],
    "from": {
        "email": "sales@example.com",
        "name": "Example Sales Team"
    },
    "headers": { "X-Message-Source": "" },
    "subject": "Your Example Order Confirmation",
    "text": "Congratulations on your order no. 1234",
    "category": "API Test"
}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Api-Token": os.getenv("EMAIL_TOKEN")
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())

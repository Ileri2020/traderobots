import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "http://localhost:8000/api/users/login/"
payload = {
    "username": "adepojuololade",
    "password": "ololade2020"
}
headers = {'Content-Type': 'application/json'}

session = requests.Session()

try:
    print(f"1. Login...")
    response = session.post(url, json=payload, headers=headers)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        print("2. Fetching Accounts...")
        acc_resp = session.get("http://localhost:8000/api/accounts/")
        print(f"Accounts Status: {acc_resp.status_code}")
        print("Accounts Data:")
        print(acc_resp.text)
except Exception as e:
    print(f"Request failed: {e}")

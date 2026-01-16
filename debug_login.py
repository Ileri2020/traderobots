import requests
import sys

# Set encoding to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

url = "http://localhost:8000/api/users/login/"
payload = {
    "username": "adepojuololade",
    "password": "ololade2020"
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Attempting login to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response JSON Hint:")
    # Print start of text safely
    print(response.text[:2000])
except Exception as e:
    print(f"Request failed: {e}")

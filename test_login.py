import requests

url = "http://localhost:8000/api/users/login/"
data = {
    "username": "adepojuololade",
    "password": "ololade2020"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    with open("error_resp.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Response saved to error_resp.html")
except Exception as e:
    print(f"Error: {e}")

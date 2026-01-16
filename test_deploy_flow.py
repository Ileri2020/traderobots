import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
base_url = "http://localhost:8000/api"

def run():
    # 1. Login
    print("1. Logging in...")
    login_resp = session.post(f"{base_url}/users/login/", json={
        "username": "adepojuololade", "password": "ololade2020"
    })
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    
    # Set CSRF Token
    if 'csrftoken' in session.cookies:
        session.headers.update({'X-CSRFToken': session.cookies['csrftoken']})
        print("CSRF Token set.")
    else:
        print("Warning: No CSRF token found in cookies.")

    # 2. Get Account ID 5 (or valid one)
    print("2. Finding Account...")
    accs = session.get(f"{base_url}/accounts/").json()
    valid_acc = next((a for a in accs if a['mt5_login'] == '100690024'), None)
    if not valid_acc:
        print("No valid account found!")
        return
    acc_id = valid_acc['id']
    print(f"Using Account ID: {acc_id} ({valid_acc['mt5_login']})")

    # 3. Create Robot
    print("3. Creating Robot...")
    robot_data = {
        "symbol": "EURUSD",
        "method": "winrate", # 'method' field based on model/serializer? Model has 'method'.
        "indicators": ["rsi"],
        "risk_settings": {"lot": 0.01, "sl": 50, "tp": 100},
        "win_rate": 80.0
    }
    robot_resp = session.post(f"{base_url}/robots/", json=robot_data)
    if robot_resp.status_code != 201:
        print(f"Robot creation failed: {robot_resp.text}")
        return
    
    robot_id = robot_resp.json()['id']
    print(f"Robot Created: ID {robot_id}")

    # 4. Deploy Robot
    print("4. Deploying Robot (Connecting to MT5)...")
    deploy_resp = session.post(f"{base_url}/robots/{robot_id}/deploy/", json={
        "account_id": acc_id
    })
    
    print(f"Deployment Status: {deploy_resp.status_code}")
    print("Response:")
    print(deploy_resp.text)

if __name__ == "__main__":
    run()

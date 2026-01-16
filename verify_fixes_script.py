import requests
import time
import json

BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/users/login/"
ROBOT_URL = f"{BASE_URL}/robots/create_winrate_robot/"
DEPLOY_URL = "{}/robots/{}/deploy/"
STATUS_URL = "{}/robots/{}/"

# 1. Login
session = requests.Session()
# Get CSRF token first
session.get(f"{BASE_URL}/users/login/")
csrftoken = session.cookies.get('csrftoken')

print("1. Logging in...")
headers = {"X-CSRFToken": csrftoken} if csrftoken else {}
    auth_response = session.post(LOGIN_URL, json={
        "username": "adepojuololade",
        "password": "password123"
    }, headers=headers)
    
    if auth_response.status_code != 200:
        print(f"Login Failed: {auth_response.status_code}")
        print(f"Response: {auth_response.text}")
        print(f"Sent headers: {headers}")
        exit(1)
        
    user_data = auth_response.json()
    print(f"Login Success. User: {user_data.get('username')}")
    
    # Get Account ID (Assuming one exists based on previous commands)
    accounts_response = session.get(f"{BASE_URL}/accounts/")
    accounts = accounts_response.json()
    if not accounts:
        print("No trading accounts found. Creating one...")
        # Create a dummy one for testing if needed, or fail
        # But we saw accounts in the shell command earlier
        exit(1)
    
    account_id = accounts[0]['id']
    print(f"Using Account ID: {account_id} ({accounts[0]['account_number']})")

    # 2. Create Robot
    print("\n2. Creating Robot...")
    robot_payload = {
        "name": "TestBot_CLI",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "indicators": ["rsi"],
        "risk": {"lot": 0.01, "sl": 50, "tp": 100}
    }
    create_response = session.post(ROBOT_URL, json=robot_payload, headers=headers)
    if create_response.status_code != 201:
        print(f"Create Failed: {create_response.text}")
        exit(1)
        
    robot_data = create_response.json()
    robot_id = robot_data['robot']['id']
    task_id = robot_data['task_id']
    print(f"Robot Created: ID {robot_id}. Build Task: {task_id}")

    # 3. Wait for Build
    print("\n3. Waiting for Build...")
    for _ in range(10):
        # Check task status (Checking robot status is easier if task endpoint not handy)
        # Using robot endpoint to check if mql5_code is populated or just wait
        time.sleep(2)
        r_resp = session.get(STATUS_URL.format(BASE_URL, robot_id))
        r_data = r_resp.json()
        if r_data.get('mql5_code'):
            print("Build Complete.")
            break
    else:
        print("Build timed out (mock build might be slow or failed)")
        
    # 4. Deploy (This is the critical test for the Error Handling Fix)
    print(f"\n4. Attempting Deployment to Account {account_id}...")
    deploy_url = DEPLOY_URL.format(BASE_URL, robot_id)
    deploy_payload = {
        "account_id": account_id,
        "risk": {"lot": 0.01}
    }
    
    deploy_response = session.post(deploy_url, json=deploy_payload, headers=headers)
    
    print(f"Deployment Status Code: {deploy_response.status_code}")
    print("\n--- DEPLOYMENT RESPONSE ---")
    # Safe print for Windows console
    try:
        print(json.dumps(deploy_response.json(), indent=2))
    except UnicodeEncodeError:
        print(json.dumps(deploy_response.json(), indent=2).encode('utf-8', errors='replace').decode('utf-8'))
    print("---------------------------")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to backend. Is it running?")
except Exception as e:
    print(f"An error occurred: {e}")

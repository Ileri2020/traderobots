
import requests
import json
import sys

BASE_URL = "https://traderobots.vercel.app"
API_URL = f"{BASE_URL}/api"

# Configure a session to persist cookies (authenticated state)
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Referer": BASE_URL,
    "Origin": BASE_URL
})

def print_result(page_name, api_name, status, details=""):
    symbol = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{symbol} [{page_name}] {api_name}: {details}")

def test_login_page():
    print("\n--- Testing Login Page APIs ---")
    
    # 1. CSRF Token (Optional but good practice if Django requires it for login)
    try:
        r = session.get(f"{API_URL}/users/login/") # Assuming a GET might return CSRF or just checking reachability
        # Note: DRF usually uses POST for login, GET might not be allowed or returns 405. 
        # But we need to hit the site to get cookies if keys depend on it.
    except Exception as e:
        pass

    # 2. Login
    login_data = {
        "username": "api_test_user",
        "password": "testpassword123"
    }
    
    # Try logging in
    response = session.post(f"{API_URL}/users/login/", json=login_data)
    
    if response.status_code == 200:
        print_result("Login Page", "User Login", "PASS", "Logged in successfully")
        return True
    elif response.status_code == 401:
         # Try registering if login fails
        print_result("Login Page", "User Login", "FAIL", "User not found, attempting registration...")
        reg_data = {
            "username": "api_test_user",
            "password": "testpassword123",
            "email": "apitest@example.com"
        }
        reg_response = session.post(f"{API_URL}/users/register/", json=reg_data)
        if reg_response.status_code == 201:
             print_result("Signup Page", "User Register", "PASS", "Created test user")
             # Login again
             response = session.post(f"{API_URL}/users/login/", json=login_data)
             if response.status_code == 200:
                 print_result("Login Page", "User Login (Retry)", "PASS", "Logged in after registration")
                 return True
        else:
             print_result("Signup Page", "User Register", "FAIL", f"Could not register: {reg_response.text}")
             return False
    else:
        print_result("Login Page", "User Login", "FAIL", f"Status: {response.status_code} - {response.text}")
        return False

def test_dashboard_page():
    print("\n--- Testing Dashboard Page APIs ---")
    
    # /api/accounts/ (Trading Accounts)
    r = session.get(f"{API_URL}/accounts/")
    if r.status_code == 200:
        print_result("Dashboard", "Get Trading Accounts", "PASS", f"Found {len(r.json())} accounts")
    else:
        print_result("Dashboard", "Get Trading Accounts", "FAIL", r.text)

    # /api/visits/ (App Visits)
    r = session.get(f"{API_URL}/visits/")
    if r.status_code == 200:
        print_result("Dashboard", "Get App Visits", "PASS", "Visits data retrieved")
    else:
        print_result("Dashboard", "Get App Visits", "FAIL", r.text)

def test_robots_page():
    print("\n--- Testing Robots/Marketplace Page APIs ---")
    
    # /api/robots/
    r = session.get(f"{API_URL}/robots/")
    if r.status_code == 200:
        print_result("Marketplace", "Get Robots", "PASS", f"Found {len(r.json())} robots")
    else:
        print_result("Marketplace", "Get Robots", "FAIL", r.text)

def test_social_page():
    print("\n--- Testing Social Page APIs ---")
    
    # /api/social/posts/
    r = session.get(f"{API_URL}/social/posts/")
    if r.status_code == 200:
        print_result("Social", "Get Posts", "PASS", f"Found {len(r.json())} posts")
    else:
        print_result("Social", "Get Posts", "FAIL", r.text)

    # Create a post
    post_data = {"content": "Automated API Test Post"}
    r = session.post(f"{API_URL}/social/posts/", json=post_data)
    if r.status_code == 201:
        print_result("Social", "Create Post", "PASS", "Post created")
    else:
        print_result("Social", "Create Post", "FAIL", r.text)

def test_chat_page():
    print("\n--- Testing Chat Page APIs ---")
    
    # /api/social/groups/
    r = session.get(f"{API_URL}/social/groups/")
    if r.status_code == 200:
        print_result("Chat", "Get Groups", "PASS", f"Found {len(r.json())} groups")
    else:
         print_result("Chat", "Get Groups", "FAIL", r.text)

def test_home_page():
    print("\n--- Testing Home Page ---")
    try:
        r = session.get(BASE_URL)
        if r.status_code == 200:
            print_result("Home Page", "Get Root", "PASS", f"Length: {len(r.text)}")
        else:
            print_result("Home Page", "Get Root", "FAIL", f"Status: {r.status_code}")
    except Exception as e:
        print_result("Home Page", "Get Root", "FAIL", str(e))

def run_tests():
    test_home_page()
    if not test_login_page():
        print("CRITICAL: Login failed. Aborting authenticated tests.")
        return
    
    test_dashboard_page()
    test_robots_page()
    test_social_page()
    test_chat_page()

if __name__ == "__main__":
    run_tests()

import requests
import re

try:
    response = requests.post('https://traderobots.vercel.app/api/users/login/', json={'username':'x','password':'y'})
    html = response.text
    print(f"Status Code: {response.status_code}")
    
    # Try to find exception value
    m = re.search(r'<pre class="exception_value">(.*?)</pre>', html, re.DOTALL)
    if m:
        print(f"Exception Value: {m.group(1).strip()}")
    else:
        # Fallback to verify logic
        print("Exception value class not found. Dumping title:")
        m_title = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        if m_title:
             print(f"Title: {m_title.group(1).strip()}")
        else:
             print("Title not found.")
             
except Exception as e:
    print(e)

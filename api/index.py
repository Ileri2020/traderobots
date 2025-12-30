import os
import sys

# Add the backend directory to sys.path so we can import traderobots  
# api/ is at root. backend/ is at root. So ../backend is correct.
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')

application = get_wsgi_application()

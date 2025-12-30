import os
import django
import random
import uuid
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')

# Compatibility hack for six
import six
django.utils.six = six

django.setup()

from django.contrib.auth.models import User
from api.models import Profile, Robot, TradingAccount
from social.models import Post, ChatGroup, Message

def populate():
    print("Populating 20 additional users and content...")
    
    # Get or create groups
    groups = list(ChatGroup.objects.all())
    if not groups:
        groups = [
            ChatGroup.objects.get_or_create(name='Forex Masters')[0],
            ChatGroup.objects.get_or_create(name='AI Devs')[0],
            ChatGroup.objects.get_or_create(name='Gold Scalpers')[0]
        ]
    
    main_user = User.objects.get(username='adepojuololade')

    for i in range(20):
        username = f"trader_{uuid.uuid4().hex[:8]}"
        password = "password123"
        email = f"{username}@example.com"
        
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {username}")
        
        # Profile
        Profile.objects.get_or_create(user=user, defaults={'bio': f"Financial rogue and AI enthusiast #{i}"})
        
        # Robot
        symbol = random.choice(['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'])
        Robot.objects.create(
            user=user,
            symbol=symbol,
            method=random.choice(['winrate', 'ml']),
            win_rate=random.randint(60, 95)
        )
        
        # Post
        Post.objects.create(
            user=user,
            content=f"Just deployed my new {symbol} robot! Backtesting looks solid. #forex #trading #ai"
        )
        
        # Chat
        for group in groups:
            if not group.members.filter(id=user.id).exists():
                group.members.add(user)
            if not group.members.filter(id=main_user.id).exists():
                group.members.add(main_user) # Ensure main user is in all groups
            
            Message.objects.create(
                group=group,
                sender=user,
                content=random.choice([
                    "Anyone watching the NFP release?",
                    "My robot just hit TP! 🚀",
                    "What's the best timeframe for Gold?",
                    "AI is definitely the future.",
                    "Hello everyone!"
                ])
            )

    print("Populate complete!")

if __name__ == '__main__':
    populate()

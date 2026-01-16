import os
import django
import random
import django.utils
try:
    import six
    django.utils.six = six
except ImportError:
    pass

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderobots.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile, TradingAccount, Robot
from social.models import Post, ChatGroup, Message
from api.security import encrypt

def populate():
    # 1. Create main user
    email = "adepojuololade2020@gmail.com"
    username = "adepojuololade"
    password = "ololade2020"
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
    profile.bio = "Main trader account"
    profile.role = 'admin'
    profile.save()
    
    print(f"User {email} created/updated.")

    # 2. Create MT5 accounts for main user
    # Demo
    login_demo = "100690024"
    try:
        acc_demo = TradingAccount.objects.get(user=user, mt5_login=login_demo)
    except TradingAccount.DoesNotExist:
        acc_demo = TradingAccount(user=user, mt5_login=login_demo)
    
    acc_demo.mt5_password = encrypt("R9JzFCyBFD@QZPT")
    acc_demo.mt5_server = "XMGlobal-MT5 5"
    acc_demo.is_demo = True
    acc_demo.is_active = True
    acc_demo.broker = "XM Global"
    acc_demo.save()

    # Real
    login_real = "110145487"
    try:
        acc_real = TradingAccount.objects.get(user=user, mt5_login=login_real)
    except TradingAccount.DoesNotExist:
        acc_real = TradingAccount(user=user, mt5_login=login_real)
    
    acc_real.mt5_password = encrypt("R9JzFCyBFD@QZPT")
    acc_real.mt5_server = "XMGlobal-MT5 2"
    acc_real.is_demo = False
    acc_real.is_active = True
    acc_real.broker = "XM Global"
    acc_real.save()
    
    print("MT5 accounts created for main user.")

    # 3. Create 10 robots for main user
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD', 'BTCUSD', 'XAUUSD', 'XAGUSD']
    for i in range(10):
        Robot.objects.create(
            user=user,
            symbol=symbols[i % len(symbols)],
            method='winrate',
            indicators=['rsi', 'ma'],
            risk_settings={'lot': 0.01, 'sl': 30, 'tp': 60},
            win_rate=random.uniform(60, 85),
            is_active=True
        )
    print("10 robots created for main user.")

    # 4. Create 20 random users
    random_users = []
    for i in range(20):
        uname = f"user_{i}"
        try:
            u = User.objects.get(username=uname)
        except User.DoesNotExist:
            u = User.objects.create(username=uname, email=f"{uname}@example.com")
        
        u.set_password("password123")
        u.save()
        
        try:
            Profile.objects.get(user=u)
        except Profile.DoesNotExist:
            Profile.objects.create(user=u)
            
        random_users.append(u)
        
        # Create 1 robot per random account
        Robot.objects.create(
            user=u,
            symbol=random.choice(symbols),
            method='winrate',
            indicators=['rsi'],
            risk_settings={'lot': 0.01, 'sl': 20, 'tp': 40},
            win_rate=random.uniform(50, 80),
            is_active=True
        )
    print("20 random users and their robots created.")

    # 5. Create groups and communities
    group_names = ["Forex Masters", "Crypto Bulls", "Algo Traders"]
    groups = []
    for name in group_names:
        try:
            group = ChatGroup.objects.get(name=name)
        except ChatGroup.DoesNotExist:
            group = ChatGroup.objects.create(name=name)
        
        group.admins.add(user)
        group.members.add(user)
        for ru in random_users:
            group.members.add(ru)
        groups.append(group)
    print("Groups created and users added.")

    # 6. Create posts and messages
    for ru in random_users:
        Post.objects.create(user=ru, content=f"Hello, I am {ru.username}! Just created my first robot.")
        # Chatting
        msg = Message.objects.create(
            group=random.choice(groups),
            sender=ru,
            content=f"Hey everyone, any tips for {random.choice(symbols)}?"
        )
    print("Posts and messages created.")

if __name__ == "__main__":
    populate()

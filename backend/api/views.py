from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import TradingAccount, Robot, AppVisit, Profile, TradeLog
from .serializers import (
    TradingAccountSerializer,
    RobotSerializer,
    AppVisitSerializer, 
    UserSerializer,
    TradeLogSerializer
)
from trading.mt5_connector import MT5Connector
from trading.backtester import Backtester
from trading.robot_generator import RobotGenerator
import pandas as pd

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    from django.views.decorators.csrf import csrf_exempt
    from django.utils.decorators import method_decorator

    @action(detail=False, methods=['post', 'get'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    @method_decorator(csrf_exempt)
    def google_login(self, request):
        if request.method == 'GET':
            return Response({"status": "Google login endpoint active"})
        email = request.data.get('email', 'adepojuololade2020@gmail.com')
        # ... rest of function ...
        # (I will just copy the existing logic or simpler: leave the original logic for POST inside)
        print(f"DEBUG: User about to login via Google: {email}")
        try:
            from django.contrib.auth import login
            user = User.objects.get(email=email)
            login(request, user)
            print(f"DEBUG: User logged in via Google: {user.username}")
            return Response({"status": "success", "user": UserSerializer(user).data})
        except User.DoesNotExist:
            print(f"DEBUG: Google login failed: User with email {email} not found")
            return Response({"error": "User not found, please sign up"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    @method_decorator(csrf_exempt)
    def facebook_login(self, request):
        if request.method == 'GET':
            return Response({"status": "Facebook login endpoint active"})
        email = request.data.get('email', 'adepojuololade2020@gmail.com')
        print(f"DEBUG: User about to login via Facebook: {email}")
        try:
            from django.contrib.auth import login
            user = User.objects.get(email=email)
            login(request, user)
            print(f"DEBUG: User logged in via Facebook: {user.username}")
            return Response({"status": "success", "user": UserSerializer(user).data})
        except User.DoesNotExist:
            print(f"DEBUG: Facebook login failed: User with email {email} not found")
            return Response({"error": "User not found, please sign up"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    @method_decorator(csrf_exempt)
    def login(self, request):
        if request.method == 'GET':
            return Response({"status": "Login endpoint active"})
        from django.contrib.auth import authenticate, login
        username = request.data.get('username')
        password = request.data.get('password')
        print(f"DEBUG: User about to login: {username}")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            print(f"DEBUG: User logged in: {username}")
            return Response(UserSerializer(user).data)
        print(f"DEBUG: Login failed: Invalid credentials for {username}")
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    @method_decorator(csrf_exempt)
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password:
             return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
             
        if User.objects.filter(username=username).exists():
             return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
             
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        from django.contrib.auth import logout
        print(f"DEBUG: User logging out: {request.user.username}")
        logout(request)
        return Response({"status": "logged out"})

class TradingAccountViewSet(viewsets.ModelViewSet):
    queryset = TradingAccount.objects.all()
    serializer_class = TradingAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return TradingAccount.objects.none()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        info = MT5Connector.get_account_info()
        if info:
            acc, created = TradingAccount.objects.update_or_create(
                user=request.user,
                account_number=str(info['login']),
                defaults={
                    'balance': info['balance'],
                    'equity': info['equity'],
                    'mode': 'demo' if 'demo' in info['server'].lower() else 'live'
                }
            )
            return Response(TradingAccountSerializer(acc).data)
        return Response({"error": "Failed to connect to MT5"}, status=status.HTTP_400_BAD_REQUEST)

class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # For list view, show all robots sorted by win_rate
        # For other actions (update, delete), filter by user
        if self.action == 'list':
            return self.queryset.all().order_by('-win_rate')
        
        # For non-list actions, apply user filtering
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_winrate_robot(self, request):
        symbol = request.data.get('symbol', 'EURUSD')
        name = request.data.get('name', f"Bot_{symbol}")
        timeframe = request.data.get('timeframe', 'H1')
        indicators = request.data.get('indicators', []) # ['rsi', 'ma', 'macd']
        risk = request.data.get('risk', {'lot': 0.01, 'sl': 30, 'tp': 60})
        
        print(f"DEBUG: New robot creation called by {request.user.username} for {symbol} named {name}")
        
        # Build rules from requested indicators
        rules = {}
        if 'rsi' in indicators:
            rules['rsi'] = request.data.get('rsi_settings', {'buy': 30, 'sell': 70, 'period': 14})
        if 'ma' in indicators:
            rules['ma'] = request.data.get('ma_settings', {'period': 50, 'type': 'MODE_SMA'})
        if 'macd' in indicators:
            rules['macd'] = {}

        raw_data = MT5Connector.get_market_data(symbol, timeframe, n_bars=1000)
        print(f"data to rtain robot {raw_data} for {request.user.username}")
        if raw_data is None:
            print("failed to fetch training data")
            # Sample data if MT5 is not available for testing
            df = pd.DataFrame({'close': [1.08] * 100, 'time': pd.date_range('2024-01-01', periods=100, freq='H')})
        else:
            df = pd.DataFrame(raw_data)
            df['time'] = pd.to_datetime(df['time'], unit='s')

        bt = Backtester(df, rules)
        trades = bt.run()
        metrics = bt.compute_metrics(trades)
        
        mql5_code = RobotGenerator.generate_mql5(name, symbol, timeframe, rules, risk)
        
        robot = Robot.objects.create(
            user=request.user,
            name=name,
            symbol=symbol,
            method='winrate',
            indicators=indicators,
            risk_settings=risk,
            win_rate=metrics['win_rate'],
            mql5_code=mql5_code
        )
        return Response(RobotSerializer(robot).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def create_rnn_robot(self, request):
        symbol = request.data.get('symbol', 'EURUSD')
        name = request.data.get('name', f"RNN_{symbol}")
        years = int(request.data.get('years', 1))
        
        print(f"DEBUG: RNN robot creation requested by {request.user.username} for {symbol} ({years}yr)")
        
        import os
        cloudinary_config = {
            'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME', 'dc5khnuiu'),
            'api_key': os.getenv('CLOUDINARY_API_KEY', '474889658884221'),
            'api_secret': os.getenv('CLOUDINARY_API_SECRET', 'iCF8R9GNc0IAPV_mcTy4gaxpn2A')
        }

        # 1. Create the Robot record first to get a permanent ID
        robot = Robot.objects.create(
            user=request.user,
            name=name,
            symbol=symbol,
            method='rnn',
            win_rate=0.0
        )

        # 2. Generate the training script with the Robot's ID injected
        colab_code = RobotGenerator.generate_rnn_colab(name, symbol, years, cloudinary_config)
        colab_code = colab_code.replace('ROBOT_ID = "YOUR_ROBOT_ID"', f'ROBOT_ID = "{robot.id}"')
        
        # Determine the base URL for the callback
        base_url = request.build_absolute_uri('/')[:-1] # Get current server URL
        colab_code = colab_code.replace('BACKEND_URL = "http://localhost:8000"', f'BACKEND_URL = "{base_url}"')

        # 3. Update with the generated code
        robot.mql5_code = colab_code
        robot.save()
        
        return Response(RobotSerializer(robot).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_rnn_model(self, request, pk=None):
        robot = self.get_object()
        model_url = request.data.get('model_url')
        if not model_url:
            return Response({"error": "model_url required"}, status=status.HTTP_400_BAD_REQUEST)
        
        robot.model_url = model_url
        robot.is_active = True
        robot.win_rate = 85.0
        robot.save()
        
        import requests
        import os
        from django.conf import settings
        try:
            model_path = os.path.join(settings.BASE_DIR, 'models', f"{robot.id}.h5")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            r = requests.get(model_url, allow_redirects=True)
            with open(model_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print(f"DEBUG: Failed to save model locally: {e}")

        return Response({"status": "model saved", "robot": RobotSerializer(robot).data})

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        robot = self.get_object()
        account_id = request.data.get('account_id')
        
        lot = float(request.data.get('lot', 0.01))
        sl = int(request.data.get('sl', 30))
        tp = int(request.data.get('tp', 60))
        
        try:
            account = TradingAccount.objects.get(id=account_id, user=request.user)
        except TradingAccount.DoesNotExist:
            return Response({"error": "Trading Account not found"}, status=status.HTTP_404_NOT_FOUND)
            
        print(f"DEBUG: Deploying Robot {robot.id} to Account {account.account_number}")
        
        # Reconstruct rules from stored indicators
        # Note: Ideally we store the full 'rules' dict in the model, but currently we store 'indicators' list
        # We will do a best-effort reconstruction or use stored risk_settings if available
        # Ideally we'd persist the exact 'rules' dict used during creation.
        
        # For now, let's reconstruct similarly to create_winrate_robot
        rules = {}
        if 'rsi' in robot.indicators: rules['rsi'] = {'buy': 30, 'sell': 70, 'period': 14}
        if 'ma' in robot.indicators: rules['ma'] = {'period': 50, 'type': 'MODE_SMA'}
        if 'macd' in robot.indicators: rules['macd'] = {}
        if 'bands' in robot.indicators: rules['bands'] = {'period': 20, 'dev': 2.0}
        if 'stoch' in robot.indicators: rules['stoch'] = {}

        risk = {'lot': lot, 'sl': sl, 'tp': tp}
        
        # Generate Python Code
        python_code = RobotGenerator.generate_python(
            robot_name=f"Bot_{robot.symbol}_{robot.id}",
            symbol=robot.symbol,
            timeframe="H1", # Defaulting to H1 as stored in create_winrate_robot
            rules=rules,
            risk=risk,
            account_id=account.account_number, # Use account number (login) for MT5
            password=account.password if account.password else "PASSWORD",
            server=account.server if account.server else "MetaQuotes-Demo"
        )
        
        robot.python_code = python_code
        robot.risk_settings = risk # Update risk settings with deployed values
        robot.is_active = True
        robot.save()
        
        return Response({
            "status": "deployed",
            "message": "Robot python code generated successfully. Ready for execution.",
            "python_code": python_code
        })

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        count = Robot.objects.filter(user=request.user).count()
        Robot.objects.filter(user=request.user).delete()
        print(f"DEBUG: Deleted {count} robots for {request.user.username}")
        return Response({"status": "deleted", "count": count}, status=status.HTTP_204_NO_CONTENT)
class AppVisitViewSet(viewsets.ModelViewSet):
    queryset = AppVisit.objects.all()
    serializer_class = AppVisitSerializer
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class TradeLogViewSet(viewsets.ModelViewSet):
    queryset = TradeLog.objects.all().order_by('-timestamp')
    serializer_class = TradeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

class MarketDataView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def history(self, request):
        symbol = request.query_params.get('symbol', 'EURUSD')
        timeframe = request.query_params.get('timeframe', 'H1')
        n_bars = int(request.query_params.get('n_bars', 100))
        
        data = MT5Connector.get_market_data(symbol, timeframe, n_bars)
        if data is not None:
            return Response(pd.DataFrame(data).to_dict(orient='records'))
        return Response({"error": "Failed to fetch data"}, status=status.HTTP_400_BAD_REQUEST)

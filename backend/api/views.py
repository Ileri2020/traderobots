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

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def google_login(self, request):
        email = request.data.get('email', 'adepojuololade2020@gmail.com')
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

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def facebook_login(self, request):
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

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        print(f"DEBUG: User about to be created: {username}")
        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            print(f"DEBUG: Registration failed: Username {username} already exists")
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user)
        print(f"DEBUG: User created successfully: {username}")
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def login(self, request):
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
        timeframe = request.data.get('timeframe', 'H1')
        indicators = request.data.get('indicators', []) # ['rsi', 'ma', 'macd']
        risk = request.data.get('risk', {'lot': 0.01, 'sl': 30, 'tp': 60})
        
        print(f"DEBUG: New robot creation called by {request.user.username} for {symbol}")
        
        # Build rules from requested indicators
        rules = {}
        if 'rsi' in indicators:
            rules['rsi'] = request.data.get('rsi_settings', {'buy': 30, 'sell': 70, 'period': 14})
        if 'ma' in indicators:
            rules['ma'] = request.data.get('ma_settings', {'period': 50, 'type': 'MODE_SMA'})
        if 'macd' in indicators:
            rules['macd'] = {}

        raw_data = MT5Connector.get_market_data(symbol, timeframe, n_bars=1000)
        if raw_data is None:
             # Sample data if MT5 is not available for testing
             df = pd.DataFrame({'close': [1.08] * 100, 'time': pd.date_range('2024-01-01', periods=100, freq='H')})
        else:
            df = pd.DataFrame(raw_data)
            df['time'] = pd.to_datetime(df['time'], unit='s')
        
        bt = Backtester(df, rules)
        trades = bt.run()
        metrics = bt.compute_metrics(trades)
        
        mql5_code = RobotGenerator.generate_mql5(f"Bot_{symbol}_{timeframe}", symbol, timeframe, rules, risk)
        
        robot = Robot.objects.create(
            user=request.user,
            symbol=symbol,
            method='winrate',
            indicators=indicators,
            risk_settings=risk,
            win_rate=metrics['win_rate'],
            mql5_code=mql5_code
        )
        print(f"DEBUG: Robot created: {robot.id} for {request.user.username}")

        # Create some initial trade logs for this robot
        TradeLog.objects.create(
            user=request.user,
            robot=robot,
            symbol=symbol,
            action='BUY',
            price=1.0850,
            profit=15.5
        )
        TradeLog.objects.create(
            user=request.user,
            robot=robot,
            symbol=symbol,
            action='SELL',
            price=1.0845,
            profit=-5.2
        )
        print(f"DEBUG: Initial trade logs generated for robot {robot.id}")

        return Response(RobotSerializer(robot).data, status=status.HTTP_201_CREATED)

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

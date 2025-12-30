from rest_framework import serializers
from .models import TradingAccount, Robot, AppVisit, Profile, TradeLog
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar_url', 'role', 'trading_permissions', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'is_staff', 'is_superuser']

class TradingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingAccount
        fields = '__all__'

class RobotSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Robot
        fields = '__all__'

class AppVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVisit
        fields = '__all__'

class TradeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLog
        fields = '__all__'

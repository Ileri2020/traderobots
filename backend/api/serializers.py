from rest_framework import serializers
from .models import (
    TradingAccount, Robot, AppVisit, Profile, TradeLog, 
    RobotBuildTask, StrategyVersion, AccountGuardrail, 
    EmergencyKillSwitch, DeploymentValidation, IndicatorTemplate, RobotEvent
)
from django.contrib.auth.models import User
from .security import encrypt

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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = TradingAccount
        fields = [
            "id", "broker", "mt5_login", "password",
            "mt5_server", "is_demo"
        ]

    def create(self, validated_data):
        raw_password = validated_data.pop("password")
        validated_data["mt5_password"] = encrypt(raw_password)
        return super().create(validated_data)

class RobotSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Robot
        fields = '__all__'
        read_only_fields = ['user']

class AppVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVisit
        fields = '__all__'

class TradeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLog
        fields = '__all__'

class RobotBuildTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotBuildTask
        fields = '__all__'

class StrategyVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategyVersion
        fields = '__all__'

class AccountGuardrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGuardrail
        fields = '__all__'

class EmergencyKillSwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyKillSwitch
        fields = '__all__'

class DeploymentValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentValidation
        fields = '__all__'

class IndicatorTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorTemplate
        fields = '__all__'

class RobotEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotEvent
        fields = '__all__'

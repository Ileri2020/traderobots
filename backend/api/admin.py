from django.contrib import admin
from .models import (
    TradingAccount, Robot, AppVisit, Profile, 
    TradeLog, RobotBuildTask, StrategyVersion,
    AccountGuardrail, EmergencyKillSwitch, DeploymentValidation,
    IndicatorTemplate, RobotEvent
)

admin.site.register(Profile)
admin.site.register(TradingAccount)
admin.site.register(Robot)
admin.site.register(AppVisit)
admin.site.register(TradeLog)
admin.site.register(RobotBuildTask)
admin.site.register(StrategyVersion)
admin.site.register(AccountGuardrail)
admin.site.register(EmergencyKillSwitch)
admin.site.register(DeploymentValidation)
admin.site.register(IndicatorTemplate)
admin.site.register(RobotEvent)

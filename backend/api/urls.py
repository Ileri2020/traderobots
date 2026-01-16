from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TradingAccountViewSet, RobotViewSet, AppVisitViewSet, MarketDataView, 
    UserViewSet, TradeLogViewSet, RobotBuildTaskViewSet,
    AccountGuardrailViewSet, EmergencyKillSwitchViewSet, 
    IndicatorTemplateViewSet
)
 
router = DefaultRouter()
router.register(r'accounts', TradingAccountViewSet)
router.register(r'robots', RobotViewSet)
router.register(r'visits', AppVisitViewSet)
router.register(r'users', UserViewSet)
router.register(r'market', MarketDataView, basename='market')
router.register(r'logs', TradeLogViewSet)
router.register(r'build-tasks', RobotBuildTaskViewSet)
router.register(r'guardrails', AccountGuardrailViewSet)
router.register(r'kill-switch', EmergencyKillSwitchViewSet)
router.register(r'indicator-templates', IndicatorTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

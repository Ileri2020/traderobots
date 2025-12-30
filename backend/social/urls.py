from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ChatGroupViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'groups', ChatGroupViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

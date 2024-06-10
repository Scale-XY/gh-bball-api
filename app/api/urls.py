# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, PlayerViewSet, GameViewSet, PlayerStatisticsViewSet


router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'player_statistics', PlayerStatisticsViewSet)

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
]

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, PlayerViewSet, GameViewSet, PlayerStatisticsViewSet, PlayerCSVUploadViewSet, UploadPlayerStatisticsViewSet
from .views import TopPlayersViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'player-statistics', PlayerStatisticsViewSet)
router.register(r'players-upload', PlayerCSVUploadViewSet, basename='player-csv-upload')
router.register(r'upload-player-statistics', UploadPlayerStatisticsViewSet, basename='csv-upload-player-statistics')
router.register(r'top-players', TopPlayersViewSet, basename='top-players')

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
]

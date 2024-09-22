# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, PlayerViewSet, GameViewSet, PlayerStatisticsViewSet, PlayerCSVUploadViewSet, UploadPlayerStatisticsViewSet
from .views import TopPlayersViewSet, PlayoffTeamsViewSet, TopPlayoffsPlayersViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'players', PlayerViewSet, basename='players')
router.register(r'games', GameViewSet, basename='games')
router.register(r'player-statistics', PlayerStatisticsViewSet, basename='player-statistics')
router.register(r'players-upload', PlayerCSVUploadViewSet, basename='player-csv-upload')
router.register(r'upload-player-statistics', UploadPlayerStatisticsViewSet, basename='csv-upload-player-statistics')
router.register(r'top-players', TopPlayersViewSet, basename='top-players')

router.register(r'playoffs', PlayoffTeamsViewSet, basename='playoffs')
router.register(r'playoffs-top-players', TopPlayoffsPlayersViewSet, basename='playoffs-top-players')

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
]

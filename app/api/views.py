# views.py
from rest_framework import viewsets
from .models import Team, Player, Game, PlayerStatistics
from .serializers import TeamSerializer, PlayerSerializer, GameSerializer, PlayerStatisticsSerializer
from rest_framework.decorators import action

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @action(detail=False, methods=['get'])
    def standings(self, request):
        teams = Team.objects.all().order_by('-wins', 'losses')
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStatistics.objects.all()
    serializer_class = PlayerStatisticsSerializer

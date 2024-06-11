# views.py
from rest_framework import viewsets
from .models import Team, Player, Game, PlayerStatistics
from .serializers import TeamSerializer, PlayerSerializer, GameSerializer, GameWithStatsSerializer
from .serializers import PlayerStatisticsSerializer, PlayerCSVSerializer, TeamWithGamesSerializer
from rest_framework.decorators import action

from rest_framework import viewsets
from rest_framework.response import Response
import csv

class PlayerCSVUploadViewSet(viewsets.ViewSet):
    permission_classes = []

    def create(self, request):
        csv_file = request.FILES.get('csv_file')
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Invalid file format. Please upload a CSV file.'}, status=400)

        players_created = 0
        players_updated = 0

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(decoded_file)
        for row in csv_reader:
            serializer = PlayerCSVSerializer(data=row)
            if serializer.is_valid():
                data = serializer.validated_data
                team_name = data.pop('team')
                team, created = Team.objects.get_or_create(name=team_name)
                player, created = Player.objects.update_or_create(name=data['name'], defaults={**data, 'team': team})
                if created:
                    players_created += 1
                else:
                    players_updated += 1
            else:
                return Response(serializer.errors, status=400)

        return Response({'players_created': players_created, 'players_updated': players_updated}, status=201)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamWithGamesSerializer
    permission_classes = []
    http_method_names = ['get']

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = []
    http_method_names = ['get']

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameWithStatsSerializer
    permission_classes = []
    http_method_names = ['get']

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStatistics.objects.all()
    serializer_class = PlayerStatisticsSerializer
    permission_classes = []
    http_method_names = ['get']

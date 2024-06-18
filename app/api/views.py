# views.py
from rest_framework import viewsets
from .models import Team, Player, Game, PlayerStatistics
from .serializers import TeamSerializer, PlayerSerializer, GameSerializer, GameWithStatsSerializer
from .serializers import PlayerStatisticsSerializer, PlayerCSVSerializer, TeamWithGamesSerializer
from rest_framework.decorators import action

from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
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
    queryset = Team.objects.all().order_by('-wins', 'losses')
    serializer_class = TeamWithGamesSerializer
    permission_classes = []
    http_method_names = ['get']

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = []
    http_method_names = ['get']

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('game_number')
    serializer_class = GameWithStatsSerializer
    permission_classes = []
    http_method_names = ['get']

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStatistics.objects.all()
    serializer_class = PlayerStatisticsSerializer
    permission_classes = []
    http_method_names = ['get']


class UploadPlayerStatisticsViewSet(viewsets.ViewSet):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file_obj.read().decode('utf-8').splitlines()

        csv_reader = csv.reader(decoded_file)
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            player_name, game_number, two_point_fg, three_point_fg, free_throw_fg, defensive_rebounds, assists, steals, blocks, fouls = row

            if not game_number:
                continue  # Skip entry if game number is blank

            # Get or create player
            player, _ = Player.objects.get_or_create(name=player_name)

            # Get or create game
            game, _ = Game.objects.get_or_create(game_number=game_number)

            # Create player statistics
            PlayerStatistics.objects.create(
                player=player,
                game=game,
                two_point_fg=two_point_fg,
                three_point_fg=three_point_fg,
                free_throw_fg=free_throw_fg,
                defensive_rebounds=defensive_rebounds,
                assists=assists,
                steals=steals,
                blocks=blocks,
                fouls=fouls
            )

        return Response({'message': 'CSV file uploaded successfully'}, status=status.HTTP_201_CREATED)


class TopPlayersViewSet(viewsets.ViewSet):
    permission_classes = []
    queryset = Player.objects.all()

    def list(self, request):
        top_points = self.queryset.order_by('-average_points_per_game')[:10]
        top_rebounds = self.queryset.order_by('-average_rebounds_per_game')[:10]
        top_assists = self.queryset.order_by('-average_assists_per_game')[:10]
        top_three_point_fg = self.queryset.order_by('-total_three_point_fg')[:10]
        top_blocks = self.queryset.order_by('-total_blocks')[:10]
        top_steals = self.queryset.order_by('-total_steals')[:10]

        serializer_points = PlayerSerializer(top_points, many=True)
        serializer_rebounds = PlayerSerializer(top_rebounds, many=True)
        serializer_assists = PlayerSerializer(top_assists, many=True)
        serializer_three_point_fg = PlayerSerializer(top_three_point_fg, many=True)
        serializer_blocks = PlayerSerializer(top_blocks, many=True)
        serializer_steals = PlayerSerializer(top_steals, many=True)

        return Response({
            'top_points_per_game': serializer_points.data,
            'top_rebounds_per_game': serializer_rebounds.data,
            'top_assists_per_game': serializer_assists.data,
            'top_three_point_fg': serializer_three_point_fg.data,
            'top_blocks_per_game': serializer_blocks.data,
            'top_steals_per_game': serializer_steals.data,
        })
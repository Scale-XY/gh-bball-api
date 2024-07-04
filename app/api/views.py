# views.py
from rest_framework import viewsets
from .models import Team, Player, Game, PlayerStatistics
from .serializers import TeamSerializer, PlayerSerializer, GameSerializer, GameWithStatsSerializer
from .serializers import PlayerStatisticsSerializer, PlayerCSVSerializer, TeamWithGamesSerializer
from rest_framework.decorators import action

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.response import Response
import csv

class PlayoffTeamsViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        playoff_stages = ['QF1', 'QF2', 'SF', 'F']
        playoff_teams = {}

        for stage in playoff_stages:
            games = Game.objects.filter(playoff_game=stage)
            teams = set()
            for game in games:
                teams.add(game.home_team)
                teams.add(game.away_team)
            playoff_teams[stage] = TeamSerializer(list(teams), many=True).data

        return Response(playoff_teams)

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

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.exclude(game_number__isnull=True).order_by('game_number')
    serializer_class = GameWithStatsSerializer
    permission_classes = []
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStatistics.objects.exclude(game__playoff_game__isnull=True).all()
    serializer_class = PlayerStatisticsSerializer
    permission_classes = []
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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

            if isinstance(game_number, str) and "F" in game_number:
                game, _ = Game.objects.get_or_create(playoff_game=game_number)
            else:
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

    def list(self, request):
        players = Player.objects.all()  # Fetch all players

        # Sort players based on different statistics using lambda functions
        top_points_per_game = sorted(players, key=lambda p: -p.average_points_per_game)[:10]
        top_rebounds_per_game = sorted(players, key=lambda p: -p.average_rebounds_per_game)[:10]
        top_assists_per_game = sorted(players, key=lambda p: -p.average_assists_per_game)[:10]
        top_three_points_made = sorted(players, key=lambda p: -p.total_three_point_fg)[:10]
        top_blocks_per_game = sorted(players, key=lambda p: -p.average_blocks_per_game)[:10]
        top_steals_per_game = sorted(players, key=lambda p: -p.average_steals_per_game)[:10]

        data = {
            'top_points_per_game': PlayerSerializer(top_points_per_game, many=True).data,
            'top_rebounds_per_game': PlayerSerializer(top_rebounds_per_game, many=True).data,
            'top_assists_per_game': PlayerSerializer(top_assists_per_game, many=True).data,
            'top_three_points_made': PlayerSerializer(top_three_points_made, many=True).data,
            'top_blocks_per_game': PlayerSerializer(top_blocks_per_game, many=True).data,
            'top_steals_per_game': PlayerSerializer(top_steals_per_game, many=True).data,
        }

        return Response(data)

class TopPlayoffsPlayersViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        players = Player.objects.all()  # Fetch all players

        # Sort players based on different statistics using lambda functions
        top_points_per_game = sorted(players, key=lambda p: -p.average_playoff_points_per_game)[:10]
        top_rebounds_per_game = sorted(players, key=lambda p: -p.average_playoff_rebounds_per_game)[:10]
        top_assists_per_game = sorted(players, key=lambda p: -p.average_playoff_assists_per_game)[:10]
        top_three_points_made = sorted(players, key=lambda p: -p.total_playoff_three_point_fg)[:10]
        top_blocks_per_game = sorted(players, key=lambda p: -p.average_playoff_blocks_per_game)[:10]
        top_steals_per_game = sorted(players, key=lambda p: -p.average_playoff_steals_per_game)[:10]

        data = {
            'top_points_per_game': PlayerSerializer(top_points_per_game, many=True).data,
            'top_rebounds_per_game': PlayerSerializer(top_rebounds_per_game, many=True).data,
            'top_assists_per_game': PlayerSerializer(top_assists_per_game, many=True).data,
            'top_three_points_made': PlayerSerializer(top_three_points_made, many=True).data,
            'top_blocks_per_game': PlayerSerializer(top_blocks_per_game, many=True).data,
            'top_steals_per_game': PlayerSerializer(top_steals_per_game, many=True).data,
        }

        return Response(data)
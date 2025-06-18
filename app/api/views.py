# views.py
from rest_framework import viewsets
from .models import Season, Team, Player, Game, PlayerStatistics
from .serializers import TeamDetailSerializer, TeamSerializer, PlayerSerializer, GameSerializer, GameWithStatsSerializer
from .serializers import PlayerStatisticsSerializer, PlayerCSVSerializer, TeamWithGamesSerializer
from .serializers import PlayerPlayoffsSerializer, TeamStandingsSerializer
from rest_framework.decorators import action

from django.db import transaction
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

class PlayoffTeamsViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer
    permission_classes = []
    http_method_names = ['get']

    def get_queryset(self):
        # Get the season from query parameters
        season_number = self.request.query_params.get('season', 1)
        # Start with the base queryset
        queryset = Game.objects.exclude(game_number__isnull=False).order_by('date')
        
        # Filter by season if provided
        if season_number:
            queryset = queryset.filter(season__number=season_number) 
        
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PlayerCSVUploadViewSet(viewsets.ViewSet):
    permission_classes = []

    def create(self, request):
        csv_file = request.FILES.get('csv_file')
        season_number = request.data.get('season')  # Get season from request data
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Invalid file format. Please upload a CSV file.'}, status=400)

        players_created = 0
        players_updated = 0

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(decoded_file)

        season = None
        if season_number:
            season, created = Season.objects.get_or_create(number=season_number)
        else:
            raise ValueError('Season number is required')
        
        for row in csv_reader:
            serializer = PlayerCSVSerializer(data=row)
            if serializer.is_valid():
                data = serializer.validated_data
                team_name = data.pop('team')

                # Get or create the team
                team, created = Team.objects.get_or_create(name=team_name, season=season)

                # Update or create the player with the associated team and season
                player, created = Player.objects.update_or_create(
                    name=data['name'],
                    season=season,
                    defaults={**data, 'team': team}
                )
                
                if created:
                    players_created += 1
                else:
                    players_updated += 1
            else:
                return Response(serializer.errors, status=400)

        return Response({'players_created': players_created, 'players_updated': players_updated}, status=201)


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = []
    http_method_names = ['get']

    def get_queryset(self):
        season_number = self.request.query_params.get('season', 1)
        if season_number:
            teams = Team.objects.filter(season__number=season_number).distinct()
        else:
            teams = Team.objects.all()
        
        # Sort teams with head-to-head tiebreaker
        return sorted(teams, key=lambda team: self._get_team_sort_key(team, teams), reverse=True)

    def _get_team_sort_key(self, team, all_teams):
        """
        Create a sort key for a team that considers:
        1. Wins (primary)
        2. Losses (secondary, lower is better)
        3. Head-to-head record against tied teams (tiebreaker)
        """
        # Primary sort: wins (higher is better)
        wins = team.wins
        
        # Secondary sort: losses (lower is better, so we negate it)
        losses = -team.losses
        
        # Find teams with the same win-loss record for head-to-head comparison
        tied_teams = [t for t in all_teams if t.wins == team.wins and t.losses == team.losses and t != team]
        
        # Calculate head-to-head wins against tied teams
        head_to_head_wins = sum(team.get_head_to_head_wins(tied_team) for tied_team in tied_teams)
        
        # Return a tuple for sorting: (wins, -losses, head_to_head_wins)
        # This ensures teams are sorted by wins first, then by fewer losses, then by head-to-head wins
        return (wins, losses, head_to_head_wins)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        elif self.action == 'list':
            return TeamStandingsSerializer
        return TeamWithGamesSerializer
    
class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    permission_classes = []
    http_method_names = ['get']

    def get_queryset(self):
        season_number = self.request.query_params.get('season', 1)
        if season_number:
            return Player.objects.filter(season__number=season_number)
        return Player.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameWithStatsSerializer
    permission_classes = []
    http_method_names = ['get']

    def get_queryset(self):
        season_number = self.request.query_params.get('season', 1)
        if season_number:
            return Game.objects.filter(season__number=season_number).order_by('-date')
        return Game.objects.all().order_by('-date')

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerStatisticsSerializer
    permission_classes = []
    http_method_names = ['get']

    def get_queryset(self):
        season_number = self.request.query_params.get('season', 1)
        if season_number:
            return PlayerStatistics.objects.filter(game__season__number=season_number).exclude(game__playoff_game__isnull=True)
        return PlayerStatistics.objects.exclude(game__playoff_game__isnull=True)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UploadPlayerStatisticsViewSet(viewsets.ViewSet):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def parse_minutes_played(self, time_str):
        if isinstance(time_str, str) and ":" in time_str:
            minutes, seconds = map(int, time_str.split(":"))
            return minutes * 60 + seconds
        return 0  # default fallback
    
    @transaction.atomic
    def create(self, request):
        file_obj = request.FILES.get('file')
        season_number = request.data.get('season')  # Get season from request data
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file_obj.read().decode('utf-8').splitlines()

        csv_reader = csv.reader(decoded_file)
        next(csv_reader)  # Skip header 
        
        season = None
        if season_number:
            season, created = Season.objects.get_or_create(number=season_number)
        else:
            raise ValueError('Season number is required')

        for row in csv_reader:

            player_name, game_number, minutes_played, two_point_fg, two_point_attempts, \
            three_point_fg, three_point_attempts, free_throw_fg, free_throw_attempts, \
            offensive_rebounds, defensive_rebounds, assists, turnovers, \
            steals, blocks, fouls, fouls_drawn, plus_minus, efficiency = row

            if not game_number:
                continue  # Skip entry if game number is blank
            
            player_name = player_name.strip()

            try:
                player = Player.objects.get(name=player_name, season=season)
            except Player.DoesNotExist:
                return Response({
                    'error': "Player not found at row",
                    'player_name': player_name,
                    'season': season_number
                }, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(game_number, str) and ("F" in game_number or "TTB" in game_number):
                game = Game.objects.get(playoff_game=game_number, season=season)
            else:
                game = Game.objects.get(game_number=game_number, season=season)

            minutes_played = self.parse_minutes_played(minutes_played)

            # Create player statistics
            PlayerStatistics.objects.update_or_create(
                player=player,
                game=game,
                defaults={
                    'minutes_played': minutes_played,
                    'two_point_fg': two_point_fg,
                    'two_point_attempts': two_point_attempts,
                    'three_point_fg': three_point_fg,
                    'three_point_attempts': three_point_attempts,
                    'free_throw_fg': free_throw_fg,
                    'free_throw_attempts': free_throw_attempts,
                    'defensive_rebounds': defensive_rebounds,
                    'offensive_rebounds': offensive_rebounds,
                    'assists': assists,
                    'turnovers': turnovers,
                    'steals': steals,
                    'blocks': blocks,
                    'fouls': fouls,
                    'fouls_drawn': fouls_drawn,
                    'plus_minus': plus_minus,
                    'efficiency': efficiency,
                }
            )

        return Response({'message': 'CSV file uploaded successfully'}, status=status.HTTP_201_CREATED)


class TopPlayersViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        season_number = request.query_params.get('season', 1)
        use_fairness_adjusted = request.query_params.get('fairness_adjusted', 'false').lower() == 'true'
        
        if season_number:
            players = Player.objects.filter(season__number=season_number)  # Filter by season
        else:
            players = Player.objects.all()  # Fetch all players

        # Sort players based on different statistics using lambda functions
        if use_fairness_adjusted:
            # Use fairness-adjusted statistics that consider team's total games played
            top_points_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_points_per_game)[:10]
            top_rebounds_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_rebounds_per_game)[:10]
            top_assists_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_assists_per_game)[:10]
            top_three_points_made = sorted(players, key=lambda p: -p.total_three_point_fg)[:10]  # Total 3PM doesn't need adjustment
            top_blocks_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_blocks_per_game)[:10]
            top_steals_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_steals_per_game)[:10]
        else:
            # Use original per-game statistics (player's games played only)
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
            'fairness_adjusted': use_fairness_adjusted,
        }

        return Response(data)

class TopPlayoffsPlayersViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        season_number = request.query_params.get('season', 1)
        use_fairness_adjusted = request.query_params.get('fairness_adjusted', 'true').lower() == 'true'
        
        if season_number:
            players = Player.objects.filter(season__number=season_number)
        else:
            players = Player.objects.all()

        # Sort players based on different statistics using lambda functions
        if use_fairness_adjusted:
            # Use fairness-adjusted playoff statistics that consider team's total playoff games played
            top_points_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_playoff_points_per_game)[:10]
            top_rebounds_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_playoff_rebounds_per_game)[:10]
            top_assists_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_playoff_assists_per_game)[:10]
            top_three_points_made = sorted(players, key=lambda p: -p.total_playoff_three_point_fg)[:10]  # Total playoff 3PM doesn't need adjustment
            top_blocks_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_playoff_blocks_per_game)[:10]
            top_steals_per_game = sorted(players, key=lambda p: -p.fairness_adjusted_playoff_steals_per_game)[:10]
        else:
            # Use original playoff per-game statistics (player's playoff games played only)
            top_points_per_game = sorted(players, key=lambda p: -p.average_playoff_points_per_game)[:10]
            top_rebounds_per_game = sorted(players, key=lambda p: -p.average_playoff_rebounds_per_game)[:10]
            top_assists_per_game = sorted(players, key=lambda p: -p.average_playoff_assists_per_game)[:10]
            top_three_points_made = sorted(players, key=lambda p: -p.total_playoff_three_point_fg)[:10]
            top_blocks_per_game = sorted(players, key=lambda p: -p.average_playoff_blocks_per_game)[:10]
            top_steals_per_game = sorted(players, key=lambda p: -p.average_playoff_steals_per_game)[:10]

        data = {
            'top_points_per_game': PlayerPlayoffsSerializer(top_points_per_game, many=True).data,
            'top_rebounds_per_game': PlayerPlayoffsSerializer(top_rebounds_per_game, many=True).data,
            'top_assists_per_game': PlayerPlayoffsSerializer(top_assists_per_game, many=True).data,
            'top_three_points_made': PlayerPlayoffsSerializer(top_three_points_made, many=True).data,
            'top_blocks_per_game': PlayerPlayoffsSerializer(top_blocks_per_game, many=True).data,
            'top_steals_per_game': PlayerPlayoffsSerializer(top_steals_per_game, many=True).data,
            'fairness_adjusted': use_fairness_adjusted,
        }

        return Response(data)
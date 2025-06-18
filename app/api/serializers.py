# serializers.py
from rest_framework import serializers
from .models import Team, Player, Game, PlayerStatistics, Season
from django.db.models import Sum


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['number']

class TeamSerializer(serializers.ModelSerializer):
    total_games_played = serializers.SerializerMethodField()
    total_regular_season_games_played = serializers.SerializerMethodField()
    total_playoff_games_played = serializers.SerializerMethodField()
    win_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'hex_color', 'wins', 'losses', 'logo_url', 'season',
                  'total_games_played', 'total_regular_season_games_played', 
                  'total_playoff_games_played', 'win_percentage']

    def get_total_games_played(self, obj):
        return obj.total_games_played

    def get_total_regular_season_games_played(self, obj):
        return obj.total_regular_season_games_played

    def get_total_playoff_games_played(self, obj):
        return obj.total_playoff_games_played

    def get_win_percentage(self, obj):
        total_games = obj.wins + obj.losses
        if total_games > 0:
            return round((obj.wins / total_games) * 100, 1)
        return 0.0

class PlayerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team', 'season']


class PlayerOnlySerializer(serializers.ModelSerializer):


    total_points = serializers.SerializerMethodField()
    total_rebounds = serializers.SerializerMethodField()
    total_assists = serializers.SerializerMethodField()
    total_steals = serializers.SerializerMethodField()
    total_blocks = serializers.SerializerMethodField()


    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team',
            'total_points', 'total_rebounds', 'total_assists', 'total_steals',
            'total_blocks', 'season']

    def get_total_points(self, obj):
        return obj.total_points

    def get_total_rebounds(self, obj):
        return obj.total_rebounds

    def get_total_assists(self, obj):
        return obj.total_assists

    def get_total_steals(self, obj):
        return obj.total_steals

    def get_total_blocks(self, obj):
        return obj.total_blocks

class PlayerSerializer(serializers.ModelSerializer):
    total_two_point_fg = serializers.SerializerMethodField()
    total_three_point_fg = serializers.SerializerMethodField()
    total_free_throw_fg = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    total_rebounds = serializers.SerializerMethodField()
    total_assists = serializers.SerializerMethodField()
    total_steals = serializers.SerializerMethodField()
    total_blocks = serializers.SerializerMethodField()
    total_fouls = serializers.SerializerMethodField()

    average_points_per_game = serializers.SerializerMethodField()
    average_rebounds_per_game = serializers.SerializerMethodField()
    average_assists_per_game = serializers.SerializerMethodField()
    average_blocks_per_game = serializers.SerializerMethodField()
    average_steals_per_game = serializers.SerializerMethodField()

    # Fairness-adjusted statistics
    fairness_adjusted_points_per_game = serializers.SerializerMethodField()
    fairness_adjusted_rebounds_per_game = serializers.SerializerMethodField()
    fairness_adjusted_assists_per_game = serializers.SerializerMethodField()
    fairness_adjusted_blocks_per_game = serializers.SerializerMethodField()
    fairness_adjusted_steals_per_game = serializers.SerializerMethodField()
    
    # Team games information
    team_total_regular_season_games = serializers.SerializerMethodField()
    games_played_ratio = serializers.SerializerMethodField()

    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'name', 'jersey_number', 'position', 'team',
                  'total_two_point_fg', 'total_three_point_fg', 'total_free_throw_fg',
                  'total_points', 'total_rebounds', 'total_assists', 'total_steals',
                  'total_blocks', 'total_fouls',
                  'average_points_per_game', 'average_rebounds_per_game', 'average_assists_per_game',
                  'average_blocks_per_game', 'average_steals_per_game',
                  'fairness_adjusted_points_per_game', 'fairness_adjusted_rebounds_per_game',
                  'fairness_adjusted_assists_per_game', 'fairness_adjusted_blocks_per_game',
                  'fairness_adjusted_steals_per_game', 'team_total_regular_season_games',
                  'games_played_ratio', 'season',
                  'total_fg_made', 'total_fg_attempted',
                  'fg_percentage', 'two_point_percentage',
                  'three_point_percentage', 'free_throw_percentage',
                  ]

    def get_total_two_point_fg(self, obj):
        return obj.total_two_point_fg

    def get_total_three_point_fg(self, obj):
        return obj.total_three_point_fg

    def get_total_free_throw_fg(self, obj):
        return obj.total_free_throw_fg

    def get_total_points(self, obj):
        return obj.total_points

    def get_total_rebounds(self, obj):
        return obj.total_rebounds

    def get_total_assists(self, obj):
        return obj.total_assists

    def get_total_steals(self, obj):
        return obj.total_steals

    def get_total_blocks(self, obj):
        return obj.total_blocks

    def get_total_fouls(self, obj):
        return obj.total_fouls

    def get_average_points_per_game(self, obj):
        return obj.average_points_per_game

    def get_average_rebounds_per_game(self, obj):
        return obj.average_rebounds_per_game

    def get_average_assists_per_game(self, obj):
        return obj.average_assists_per_game

    def get_average_blocks_per_game(self, obj):
        return obj.average_blocks_per_game

    def get_average_steals_per_game(self, obj):
        return obj.average_steals_per_game

    def get_total_fg_made(self, obj):
        return obj.total_fg_made

    def get_total_fg_attempted(self, obj):
        return obj.total_fg_attempted

    def get_fg_percentage(self, obj):
        return obj.fg_percentage

    def get_two_point_percentage(self, obj):
        return obj.two_point_percentage

    def get_three_point_percentage(self, obj):
        return obj.three_point_percentage

    def get_free_throw_percentage(self, obj):
        return obj.free_throw_percentage

    def get_fairness_adjusted_points_per_game(self, obj):
        return obj.fairness_adjusted_points_per_game

    def get_fairness_adjusted_rebounds_per_game(self, obj):
        return obj.fairness_adjusted_rebounds_per_game

    def get_fairness_adjusted_assists_per_game(self, obj):
        return obj.fairness_adjusted_assists_per_game

    def get_fairness_adjusted_blocks_per_game(self, obj):
        return obj.fairness_adjusted_blocks_per_game

    def get_fairness_adjusted_steals_per_game(self, obj):
        return obj.fairness_adjusted_steals_per_game

    def get_team_total_regular_season_games(self, obj):
        return obj.team_total_regular_season_games

    def get_games_played_ratio(self, obj):
        return obj.games_played_ratio

class PlayerPlayoffsSerializer(serializers.ModelSerializer):
    total_playoff_two_point_fg = serializers.SerializerMethodField()
    total_playoff_three_point_fg = serializers.SerializerMethodField()
    total_playoff_free_throw_fg = serializers.SerializerMethodField()
    total_playoff_points = serializers.SerializerMethodField()
    total_playoff_rebounds = serializers.SerializerMethodField()
    total_playoff_assists = serializers.SerializerMethodField()
    total_playoff_steals = serializers.SerializerMethodField()
    total_playoff_blocks = serializers.SerializerMethodField()
    total_playoff_fouls = serializers.SerializerMethodField()

    average_playoff_points_per_game = serializers.SerializerMethodField()
    average_playoff_rebounds_per_game = serializers.SerializerMethodField()
    average_playoff_assists_per_game = serializers.SerializerMethodField()
    average_playoff_blocks_per_game = serializers.SerializerMethodField()
    average_playoff_steals_per_game = serializers.SerializerMethodField()

    # Fairness-adjusted playoff statistics
    fairness_adjusted_playoff_points_per_game = serializers.SerializerMethodField()
    fairness_adjusted_playoff_rebounds_per_game = serializers.SerializerMethodField()
    fairness_adjusted_playoff_assists_per_game = serializers.SerializerMethodField()
    fairness_adjusted_playoff_blocks_per_game = serializers.SerializerMethodField()
    fairness_adjusted_playoff_steals_per_game = serializers.SerializerMethodField()
    
    # Team playoff games information
    team_total_playoff_games = serializers.SerializerMethodField()
    playoff_games_played_ratio = serializers.SerializerMethodField()

    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team',
                  'total_playoff_two_point_fg', 'total_playoff_three_point_fg', 'total_playoff_free_throw_fg',
                  'total_playoff_points', 'total_playoff_rebounds', 'total_playoff_assists', 'total_playoff_steals',
                  'total_playoff_blocks', 'total_playoff_fouls',
                  'average_playoff_points_per_game', 'average_playoff_rebounds_per_game', 'average_playoff_assists_per_game',
                  'average_playoff_blocks_per_game', 'average_playoff_steals_per_game',
                  'fairness_adjusted_playoff_points_per_game', 'fairness_adjusted_playoff_rebounds_per_game',
                  'fairness_adjusted_playoff_assists_per_game', 'fairness_adjusted_playoff_blocks_per_game',
                  'fairness_adjusted_playoff_steals_per_game', 'team_total_playoff_games',
                  'playoff_games_played_ratio', 'season']

    def get_total_playoff_two_point_fg(self, obj):
        return obj.total_playoff_two_point_fg

    def get_total_playoff_three_point_fg(self, obj):
        return obj.total_playoff_three_point_fg

    def get_total_playoff_free_throw_fg(self, obj):
        return obj.total_playoff_free_throw_fg

    def get_total_playoff_points(self, obj):
        return obj.total_playoff_points

    def get_total_playoff_rebounds(self, obj):
        return obj.total_playoff_rebounds

    def get_total_playoff_assists(self, obj):
        return obj.total_playoff_assists

    def get_total_playoff_steals(self, obj):
        return obj.total_playoff_steals

    def get_total_playoff_blocks(self, obj):
        return obj.total_playoff_blocks

    def get_total_playoff_fouls(self, obj):
        return obj.total_playoff_fouls

    def get_average_playoff_points_per_game(self, obj):
        return obj.average_playoff_points_per_game

    def get_average_playoff_rebounds_per_game(self, obj):
        return obj.average_playoff_rebounds_per_game

    def get_average_playoff_assists_per_game(self, obj):
        return obj.average_playoff_assists_per_game

    def get_average_playoff_blocks_per_game(self, obj):
        return obj.average_playoff_blocks_per_game

    def get_average_playoff_steals_per_game(self, obj):
        return obj.average_playoff_steals_per_game

    def get_fairness_adjusted_playoff_points_per_game(self, obj):
        return obj.fairness_adjusted_playoff_points_per_game

    def get_fairness_adjusted_playoff_rebounds_per_game(self, obj):
        return obj.fairness_adjusted_playoff_rebounds_per_game

    def get_fairness_adjusted_playoff_assists_per_game(self, obj):
        return obj.fairness_adjusted_playoff_assists_per_game

    def get_fairness_adjusted_playoff_blocks_per_game(self, obj):
        return obj.fairness_adjusted_playoff_blocks_per_game

    def get_fairness_adjusted_playoff_steals_per_game(self, obj):
        return obj.fairness_adjusted_playoff_steals_per_game

    def get_team_total_playoff_games(self, obj):
        return obj.team_total_playoff_games

    def get_playoff_games_played_ratio(self, obj):
        return obj.playoff_games_played_ratio

class GameSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()
    winner = TeamSerializer()

    class Meta:
        model = Game
        fields = '__all__'

class PlayerStatisticsSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()
    total_rebounds = serializers.SerializerMethodField()
    field_goals_made = serializers.SerializerMethodField()
    field_goals_attempted = serializers.SerializerMethodField()
    field_goal_percentage = serializers.SerializerMethodField()
    two_point_percentage = serializers.SerializerMethodField()
    three_point_percentage = serializers.SerializerMethodField()
    free_throw_percentage = serializers.SerializerMethodField()

    player = PlayerDetailSerializer()

    class Meta:
        model = PlayerStatistics
        fields = ['player', 'game', 'two_point_fg', 'three_point_fg', 'free_throw_fg',
                  'offensive_rebounds', 'defensive_rebounds', 'assists', 'turnovers', 'steals', 'blocks', 'fouls',
                  'total_points', 'total_rebounds',
                  'field_goals_made', 'field_goals_attempted', 'field_goal_percentage', 'two_point_percentage', 'three_point_percentage', 'free_throw_percentage']

    def get_total_points(self, obj):
        return obj.total_points

    def get_total_rebounds(self, obj):
        return obj.total_rebounds

    def get_field_goals_made(self, obj):
        return obj.field_goals_made

    def get_field_goals_attempted(self, obj):
        return obj.field_goals_attempted

    def get_field_goal_percentage(self, obj):
        return obj.field_goal_percentage

    def get_two_point_percentage(self, obj):
        return obj.two_point_percentage

    def get_three_point_percentage(self, obj):
        return obj.three_point_percentage

    def get_free_throw_percentage(self, obj):
        return obj.free_throw_percentage

class TeamDetailSerializer(serializers.ModelSerializer):
    player_statistics = serializers.SerializerMethodField()
    team_stats = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'hex_color', 'wins', 'losses', 'logo_url', 'season',
            'player_statistics', 'team_stats'
        ]

    def get_player_statistics(self, obj):
        stats = PlayerStatistics.objects.filter(player__team=obj)
        return PlayerStatisticsSerializer(stats, many=True).data

    def get_team_stats(self, obj):
        stats = PlayerStatistics.objects.filter(player__team=obj)

        def sum_stat(field):
            return stats.aggregate(total=Sum(field))['total'] or 0

        return {
            'total_points': sum((s.total_points for s in stats), 0),
            'total_rebounds': sum((s.total_rebounds for s in stats), 0),
            'total_assists': sum_stat('assists'),
            'total_blocks': sum_stat('blocks'),
            'total_steals': sum_stat('steals'),
            'total_turnovers': sum_stat('turnovers'),
            'total_fouls': sum_stat('fouls'),
        }
    
class GameWithStatsSerializer(serializers.ModelSerializer):
    player_statistics = PlayerStatisticsSerializer(many=True, read_only=True)
    home_team = TeamSerializer()
    away_team = TeamSerializer()
    winner = TeamSerializer()
    
    class Meta:
        model = Game
        fields = '__all__'

class TeamWithGamesSerializer(serializers.ModelSerializer):
    games = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'hex_color', 'wins', 'losses', 'logo_url', 'season', 'games']  

    def get_games(self, obj):
        home_games = obj.home_games.all()
        away_games = obj.away_games.all()
        all_games = list(home_games) + list(away_games)   
        # Sort by game number, placing None values at the end
        sorted_games = sorted(all_games, key=lambda game: (game.game_number is None, game.game_number))
        return GameSerializer(sorted_games, many=True).data

class PlayerCSVSerializer(serializers.Serializer):
    name = serializers.CharField()
    position = serializers.CharField()
    team = serializers.CharField()
    jersey_number = serializers.IntegerField()

class TeamStandingsSerializer(serializers.ModelSerializer):
    total_games_played = serializers.SerializerMethodField()
    total_regular_season_games_played = serializers.SerializerMethodField()
    total_playoff_games_played = serializers.SerializerMethodField()
    win_percentage = serializers.SerializerMethodField()
    head_to_head_records = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'hex_color', 'wins', 'losses', 'logo_url', 'season',
                  'total_games_played', 'total_regular_season_games_played', 
                  'total_playoff_games_played', 'win_percentage', 'head_to_head_records']

    def get_total_games_played(self, obj):
        return obj.total_games_played

    def get_total_regular_season_games_played(self, obj):
        return obj.total_regular_season_games_played

    def get_total_playoff_games_played(self, obj):
        return obj.total_playoff_games_played

    def get_win_percentage(self, obj):
        total_games = obj.wins + obj.losses
        if total_games > 0:
            return round((obj.wins / total_games) * 100, 1)
        return 0.0

    def get_head_to_head_records(self, obj):
        """Get head-to-head records against all other teams in the same season"""
        season_teams = Team.objects.filter(season=obj.season).exclude(id=obj.id)
        records = {}
        
        for other_team in season_teams:
            wins, losses = obj.get_head_to_head_record(other_team)
            if wins > 0 or losses > 0:  # Only include teams they've played against
                records[other_team.name] = {
                    'wins': wins,
                    'losses': losses,
                    'win_percentage': obj.get_head_to_head_win_percentage(other_team)
                }
        
        return records
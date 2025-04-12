# serializers.py
from rest_framework import serializers
from .models import Team, Player, Game, PlayerStatistics, Season


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['number']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

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

    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'name', 'jersey_number', 'position', 'team',
                  'total_two_point_fg', 'total_three_point_fg', 'total_free_throw_fg',
                  'total_points', 'total_rebounds', 'total_assists', 'total_steals',
                  'total_blocks', 'total_fouls',
                  'average_points_per_game', 'average_rebounds_per_game', 'average_assists_per_game',
                  'average_blocks_per_game', 'average_steals_per_game', 'season',
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

    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team',
                  'total_playoff_two_point_fg', 'total_playoff_three_point_fg', 'total_playoff_free_throw_fg',
                  'total_playoff_points', 'total_playoff_rebounds', 'total_playoff_assists', 'total_playoff_steals',
                  'total_playoff_blocks', 'total_playoff_fouls',
                  'average_playoff_points_per_game', 'average_playoff_rebounds_per_game', 'average_playoff_assists_per_game',
                  'average_playoff_blocks_per_game', 'average_playoff_steals_per_game', 'season']

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
    total_fg_made = serializers.SerializerMethodField()
    total_fg_attempted = serializers.SerializerMethodField()
    fg_percentage = serializers.SerializerMethodField()
    two_point_percentage = serializers.SerializerMethodField()
    three_point_percentage = serializers.SerializerMethodField()
    free_throw_percentage = serializers.SerializerMethodField()

    player = PlayerDetailSerializer()

    class Meta:
        model = PlayerStatistics
        fields = ['player', 'game', 'two_point_fg', 'three_point_fg', 'free_throw_fg',
                  'offensive_rebounds', 'defensive_rebounds', 'assists', 'steals', 'blocks', 'fouls',
                  'total_points', 'total_rebounds',
                  'total_fg_made', 'total_fg_attempted', 'fg_percentage', 'two_point_percentage', 'three_point_percentage', 'free_throw_percentage']

    def get_total_points(self, obj):
        return obj.total_points

    def get_total_rebounds(self, obj):
        return obj.total_rebounds

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
        fields = ['name', 'hex_color', 'wins', 'losses', 'logo_url', 'season', 'games']  

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
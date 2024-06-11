# serializers.py
from rest_framework import serializers
from .models import Team, Player, Game, PlayerStatistics

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team']


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
            'total_blocks']

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

    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'team',
                  'total_two_point_fg', 'total_three_point_fg', 'total_free_throw_fg',
                  'total_points', 'total_rebounds', 'total_assists', 'total_steals',
                  'total_blocks', 'total_fouls']

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
    
    player = PlayerDetailSerializer()

    class Meta:
        model = PlayerStatistics
        fields = ['player', 'game', 'two_point_fg', 'three_point_fg', 'free_throw_fg',
                  'offensive_rebounds', 'defensive_rebounds', 'assists', 'steals', 'blocks', 'fouls',
                  'total_points', 'total_rebounds']

    def get_total_points(self, obj):
        return obj.total_points

    def get_total_rebounds(self, obj):
        return obj.total_rebounds

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
        fields = '__all__'

    def get_games(self, obj):
        home_games = obj.home_games.all()
        away_games = obj.away_games.all()
        all_games = list(home_games) + list(away_games)
        return GameSerializer(all_games, many=True).data

class PlayerCSVSerializer(serializers.Serializer):
    name = serializers.CharField()
    position = serializers.CharField()
    team = serializers.CharField()
    jersey_number = serializers.IntegerField()
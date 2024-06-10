# serializers.py
from rest_framework import serializers
from .models import Team, Player, Game, PlayerStatistics

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class PlayerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatistics
        fields = '__all__'

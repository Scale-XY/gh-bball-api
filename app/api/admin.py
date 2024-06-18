from django.contrib import admin
from .models import Team, Game, Player, PlayerStatistics

# In your app's admin.py file
from django.core.cache import cache

def clear_cache(modeladmin, request, queryset):
    cache.clear()

clear_cache.short_description = "Clear cache"

admin.site.add_action(clear_cache, "clear_cache")

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_color', 'wins', 'losses')
    search_fields = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('game_number', 'date', 'home_team', 'away_team', 'home_team_score', 'away_team_score', 'winner')
    list_filter = ('date', 'home_team', 'away_team')
    search_fields = ('game_number',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'jersey_number', 'position', 'team')
    list_filter = ('team', 'position')
    search_fields = ('name', 'jersey_number')

@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'two_point_fg', 'three_point_fg', 'free_throw_fg', 'offensive_rebounds', 'defensive_rebounds', 'assists', 'steals', 'blocks', 'fouls')
    list_filter = ('player', 'game')
    search_fields = ('player__name', 'game__game_number')

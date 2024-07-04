# models.py
from django.db import models
from django.db.models import Sum

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hex_color = models.CharField(max_length=255, null=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Game(models.Model):
    QUARTER_FINAL_1 = 'QF1'
    QUARTER_FINAL_2 = 'QF2'
    SEMI_FINAL_1 = 'SF1'
    SEMI_FINAL_2 = 'SF2'
    FINAL = 'F'
    PLAYOFF_CHOICES = [
        (QUARTER_FINAL_1, 'Quarterfinal 1'),
        (QUARTER_FINAL_2, 'Quarterfinal 2'),
        (SEMI_FINAL_1, 'Semifinal 1'),
        (SEMI_FINAL_2, 'Semifinal 2'),
        (FINAL, 'Final'),
    ]

    playoff_game = models.CharField(max_length=3, choices=PLAYOFF_CHOICES, null=True, blank=True)

    game_number = models.PositiveIntegerField(blank=True, null=True)

    date = models.DateTimeField(null=True)
    home_team = models.ForeignKey(Team, related_name='home_games', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_games', on_delete=models.CASCADE)
    home_team_score = models.PositiveIntegerField(default=0)
    away_team_score = models.PositiveIntegerField(default=0)
    winner = models.ForeignKey(Team, related_name='won_games', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.home_team_score > self.away_team_score:
            self.winner = self.home_team
        elif self.away_team_score > self.home_team_score:
            self.winner = self.away_team
        else:
            self.winner = None
        super().save(*args, **kwargs)


class Player(models.Model):
    name = models.CharField(max_length=255, null=True)
    jersey_number = models.IntegerField(null=True)
    position = models.CharField(max_length=255, null=True)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.jersey_number}"

    @property
    def total_two_point_fg(self):
        return self.statistics.aggregate(total_two_point_fg=Sum('two_point_fg'))['total_two_point_fg'] or 0

    @property
    def total_three_point_fg(self):
        return self.statistics.aggregate(total_three_point_fg=Sum('three_point_fg'))['total_three_point_fg'] or 0

    @property
    def total_free_throw_fg(self):
        return self.statistics.aggregate(total_free_throw_fg=Sum('free_throw_fg'))['total_free_throw_fg'] or 0

    @property
    def total_points(self):
        stats = self.statistics.aggregate(
            total_two_point_fg=Sum('two_point_fg'),
            total_three_point_fg=Sum('three_point_fg'),
            total_free_throw_fg=Sum('free_throw_fg')
        )
        total_two_point_fg = stats['total_two_point_fg'] or 0
        total_three_point_fg = stats['total_three_point_fg'] or 0
        total_free_throw_fg = stats['total_free_throw_fg'] or 0
        return (total_two_point_fg * 2) + (total_three_point_fg * 3) + total_free_throw_fg

    @property
    def total_rebounds(self):
        stats = self.statistics.aggregate(
            total_offensive_rebounds=Sum('offensive_rebounds'),
            total_defensive_rebounds=Sum('defensive_rebounds')
        )
        total_offensive_rebounds = stats['total_offensive_rebounds'] or 0
        total_defensive_rebounds = stats['total_defensive_rebounds'] or 0
        return total_offensive_rebounds + total_defensive_rebounds

    @property
    def total_assists(self):
        return self.statistics.aggregate(total_assists=Sum('assists'))['total_assists'] or 0

    @property
    def total_steals(self):
        return self.statistics.aggregate(total_steals=Sum('steals'))['total_steals'] or 0

    @property
    def total_blocks(self):
        return self.statistics.aggregate(total_blocks=Sum('blocks'))['total_blocks'] or 0

    @property
    def total_fouls(self):
        return self.statistics.aggregate(total_fouls=Sum('fouls'))['total_fouls'] or 0

    @property
    def average_points_per_game(self):
        total_games = self.statistics.count()
        if total_games > 0:
            return round(self.total_points / total_games, 1)
        else:
            return 0

    @property
    def average_rebounds_per_game(self):
        total_games = self.statistics.count()
        if total_games > 0:
            return round(self.total_rebounds / total_games, 1)
        else:
            return 0

    @property
    def average_assists_per_game(self):
        total_games = self.statistics.count()
        if total_games > 0:
            return round(self.total_assists / total_games, 1)
        else:
            return 0

    @property
    def average_blocks_per_game(self):
        total_games = self.statistics.count()
        if total_games > 0:
            return round(self.total_blocks / total_games, 1)
        else:
            return 0

    @property
    def average_steals_per_game(self):
        total_games = self.statistics.count()
        if total_games > 0:
            return round(self.total_steals / total_games, 1)
        else:
            return 0

class PlayerStatistics(models.Model):
    player = models.ForeignKey(Player, related_name='statistics', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='player_statistics', on_delete=models.CASCADE)

    two_point_fg = models.PositiveIntegerField(default=0)
    three_point_fg = models.PositiveIntegerField(default=0)
    free_throw_fg = models.PositiveIntegerField(default=0)

    offensive_rebounds = models.PositiveIntegerField(default=0)
    defensive_rebounds = models.PositiveIntegerField(default=0)

    assists = models.PositiveIntegerField(default=0)
    steals = models.PositiveIntegerField(default=0)
    blocks = models.PositiveIntegerField(default=0)
    fouls = models.PositiveIntegerField(default=0)

    @property
    def total_points(self):
        return (self.two_point_fg * 2) + (self.three_point_fg * 3) + self.free_throw_fg

    @property
    def total_rebounds(self):
        return self.offensive_rebounds + self.defensive_rebounds

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return f"{self.player} - {self.game}"

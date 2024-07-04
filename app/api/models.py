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

    def _get_statistics(self, playoff=False):
        if playoff:
            return self.statistics.filter(game__playoff_game__isnull=False)
        return self.statistics.filter(game__playoff_game__isnull=True)

    def _aggregate_statistics(self, stat_field, playoff=False):
        return self._get_statistics(playoff).aggregate(total=Sum(stat_field))['total'] or 0

    @property
    def total_two_point_fg(self):
        return self._aggregate_statistics('two_point_fg')

    @property
    def total_three_point_fg(self):
        return self._aggregate_statistics('three_point_fg')

    @property
    def total_free_throw_fg(self):
        return self._aggregate_statistics('free_throw_fg')

    @property
    def total_points(self):
        return (
            self.total_two_point_fg * 2 +
            self.total_three_point_fg * 3 +
            self.total_free_throw_fg
        )

    @property
    def total_rebounds(self):
        return (
            self._aggregate_statistics('offensive_rebounds') +
            self._aggregate_statistics('defensive_rebounds')
        )

    @property
    def total_assists(self):
        return self._aggregate_statistics('assists')

    @property
    def total_steals(self):
        return self._aggregate_statistics('steals')

    @property
    def total_blocks(self):
        return self._aggregate_statistics('blocks')

    @property
    def total_fouls(self):
        return self._aggregate_statistics('fouls')

    @property
    def average_points_per_game(self):
        total_games = self._get_statistics().count()
        if total_games > 0:
            return round(self.total_points / total_games, 1)
        return 0

    @property
    def average_rebounds_per_game(self):
        total_games = self._get_statistics().count()
        if total_games > 0:
            return round(self.total_rebounds / total_games, 1)
        return 0

    @property
    def average_assists_per_game(self):
        total_games = self._get_statistics().count()
        if total_games > 0:
            return round(self.total_assists / total_games, 1)
        return 0

    @property
    def average_blocks_per_game(self):
        total_games = self._get_statistics().count()
        if total_games > 0:
            return round(self.total_blocks / total_games, 1)
        return 0

    @property
    def average_steals_per_game(self):
        total_games = self._get_statistics().count()
        if total_games > 0:
            return round(self.total_steals / total_games, 1)
        return 0

    # Playoff statistics
    @property
    def total_playoff_two_point_fg(self):
        return self._aggregate_statistics('two_point_fg', playoff=True)

    @property
    def total_playoff_three_point_fg(self):
        return self._aggregate_statistics('three_point_fg', playoff=True)

    @property
    def total_playoff_free_throw_fg(self):
        return self._aggregate_statistics('free_throw_fg', playoff=True)

    @property
    def total_playoff_points(self):
        return (
            self.total_playoff_two_point_fg * 2 +
            self.total_playoff_three_point_fg * 3 +
            self.total_playoff_free_throw_fg
        )

    @property
    def total_playoff_rebounds(self):
        return (
            self._aggregate_statistics('offensive_rebounds', playoff=True) +
            self._aggregate_statistics('defensive_rebounds', playoff=True)
        )

    @property
    def total_playoff_assists(self):
        return self._aggregate_statistics('assists', playoff=True)

    @property
    def total_playoff_steals(self):
        return self._aggregate_statistics('steals', playoff=True)

    @property
    def total_playoff_blocks(self):
        return self._aggregate_statistics('blocks', playoff=True)

    @property
    def total_playoff_fouls(self):
        return self._aggregate_statistics('fouls', playoff=True)

    @property
    def average_playoff_points_per_game(self):
        total_games = self._get_statistics(playoff=True).count()
        if total_games > 0:
            return round(self.total_playoff_points / total_games, 1)
        return 0

    @property
    def average_playoff_rebounds_per_game(self):
        total_games = self._get_statistics(playoff=True).count()
        if total_games > 0:
            return round(self.total_playoff_rebounds / total_games, 1)
        return 0

    @property
    def average_playoff_assists_per_game(self):
        total_games = self._get_statistics(playoff=True).count()
        if total_games > 0:
            return round(self.total_playoff_assists / total_games, 1)
        return 0

    @property
    def average_playoff_blocks_per_game(self):
        total_games = self._get_statistics(playoff=True).count()
        if total_games > 0:
            return round(self.total_playoff_blocks / total_games, 1)
        return 0

    @property
    def average_playoff_steals_per_game(self):
        total_games = self._get_statistics(playoff=True).count()
        if total_games > 0:
            return round(self.total_playoff_steals / total_games, 1)
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

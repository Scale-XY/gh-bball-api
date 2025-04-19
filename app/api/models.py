# models.py
from django.db import models
from django.db.models import Sum

def get_default_season_id():
    # Get the first season or create a new one if none exists
    season, created = Season.objects.get_or_create(number=1)
    return season.id


class Season(models.Model):
    number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.number)
    
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hex_color = models.CharField(max_length=255, null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    logo_url = models.URLField(max_length=255, null=True, blank=True)  # optional logo URL
    season = models.ForeignKey(Season, 
                                default=get_default_season_id,
                                related_name='teams', on_delete=models.CASCADE)  # new season field

    class Meta:
        unique_together = ('name', 'season')  # A team name can only be unique within a season

    def __str__(self):
        return self.name

class Game(models.Model):
    QUARTER_FINAL_1 = 'QF1'
    QUARTER_FINAL_2 = 'QF2'
    QUARTER_FINAL_3 = 'QF3'
    QUARTER_FINAL_4 = 'QF4'
    TTB = 'TTB'
    SEMI_FINAL_1 = 'SF1'
    SEMI_FINAL_2 = 'SF2'
    BF3 = 'BF3'
    FINAL = 'F'
    PLAYOFF_CHOICES = [
        (QUARTER_FINAL_1, 'Quarterfinal 1'),
        (QUARTER_FINAL_2, 'Quarterfinal 2'),
        (QUARTER_FINAL_3, 'Quarterfinal 3'),
        (QUARTER_FINAL_4, 'Quarterfinal 4'),
        (TTB, 'TTB'),
        (SEMI_FINAL_1, 'Semifinal 1'),
        (SEMI_FINAL_2, 'Semifinal 2'),
        (BF3, 'BF3'),
        (FINAL, 'Final'),
    ]

    season = models.ForeignKey(Season, 
                                default=get_default_season_id,
                                related_name='games', on_delete=models.CASCADE)

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
    season = models.ForeignKey(Season, 
                                default=get_default_season_id,
                                related_name='players', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'season')  # A player name can only be unique within a season

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

    @property
    def total_fg_made(self):
        return self.total_two_point_fg + self.total_three_point_fg

    @property
    def total_fg_attempted(self):
        two_point_attempts = self._aggregate_statistics('two_point_attempts')
        three_point_attempts = self._aggregate_statistics('three_point_attempts')
        return two_point_attempts + three_point_attempts

    @property
    def fg_percentage(self):
        attempts = self.total_fg_attempted
        return round((self.total_fg_made / attempts) * 100, 1) if attempts else 0.0

    @property
    def two_point_percentage(self):
        attempts = self._aggregate_statistics('two_point_attempts')
        return round((self.total_two_point_fg / attempts) * 100, 1) if attempts else 0.0

    @property
    def three_point_percentage(self):
        attempts = self._aggregate_statistics('three_point_attempts')
        return round((self.total_three_point_fg / attempts) * 100, 1) if attempts else 0.0

    @property
    def free_throw_percentage(self):
        made = self.total_free_throw_fg
        attempts = self._aggregate_statistics('free_throw_attempts')
        return round((made / attempts) * 100, 1) if attempts else 0.0


class PlayerStatistics(models.Model):
    player = models.ForeignKey(Player, related_name='statistics', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='player_statistics', on_delete=models.CASCADE)

    minutes_played = models.PositiveIntegerField(default=0)  # this is total seconds

    two_point_fg = models.PositiveIntegerField(default=0)       # 2p_m
    two_point_attempts = models.PositiveIntegerField(default=0) # 2p_a

    three_point_fg = models.PositiveIntegerField(default=0)       # 3p_m
    three_point_attempts = models.PositiveIntegerField(default=0) # 3p_a

    free_throw_fg = models.PositiveIntegerField(default=0)       # ft_m
    free_throw_attempts = models.PositiveIntegerField(default=0) # ft_a

    offensive_rebounds = models.PositiveIntegerField(default=0)  # or
    defensive_rebounds = models.PositiveIntegerField(default=0)  # df

    assists = models.PositiveIntegerField(default=0)             # as
    turnovers = models.PositiveIntegerField(default=0)           # to
    steals = models.PositiveIntegerField(default=0)              # st
    blocks = models.PositiveIntegerField(default=0)              # bs
    fouls = models.PositiveIntegerField(default=0)               # pf
    fouls_drawn = models.PositiveIntegerField(default=0)         # fd

    plus_minus = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Allows values like 123.45 or 0.20
    efficiency = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Allows values like 123.45 or 0.20

    @property
    def total_points(self):
        return (self.two_point_fg * 2) + (self.three_point_fg * 3) + self.free_throw_fg

    @property
    def total_rebounds(self):
        return self.offensive_rebounds + self.defensive_rebounds

    @property
    def field_goals_made(self):
        return self.two_point_fg + self.three_point_fg

    @property
    def field_goals_attempted(self):
        return self.two_point_attempts + self.three_point_attempts

    @property
    def field_goal_percentage(self):
        attempts = self.field_goals_attempted
        return round((self.field_goals_made / attempts) * 100, 1) if attempts else 0.0

    @property
    def two_point_percentage(self):
        return round((self.two_point_fg / self.two_point_attempts) * 100, 1) if self.two_point_attempts else 0.0

    @property
    def three_point_percentage(self):
        return round((self.three_point_fg / self.three_point_attempts) * 100, 1) if self.three_point_attempts else 0.0

    @property
    def free_throw_percentage(self):
        return round((self.free_throw_fg / self.free_throw_attempts) * 100, 1) if self.free_throw_attempts else 0.0

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return f"{self.player} - {self.game}"

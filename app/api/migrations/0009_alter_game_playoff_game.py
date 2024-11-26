# Generated by Django 4.2.4 on 2024-11-05 15:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_alter_team_hex_color"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="playoff_game",
            field=models.CharField(
                blank=True,
                choices=[
                    ("QF1", "Quarterfinal 1"),
                    ("QF2", "Quarterfinal 2"),
                    ("QF3", "Quarterfinal 3"),
                    ("QF4", "Quarterfinal 4"),
                    ("SF1", "Semifinal 1"),
                    ("SF2", "Semifinal 2"),
                    ("F", "Final"),
                ],
                max_length=3,
                null=True,
            ),
        ),
    ]
# Generated by Django 4.2.4 on 2024-07-04 11:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_alter_team_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="playoff_game",
            field=models.CharField(
                blank=True,
                choices=[
                    ("QF1", "Quarterfinal 1"),
                    ("QF2", "Quarterfinal 2"),
                    ("SF", "Semifinal"),
                    ("F", "Final"),
                ],
                max_length=3,
                null=True,
            ),
        ),
    ]

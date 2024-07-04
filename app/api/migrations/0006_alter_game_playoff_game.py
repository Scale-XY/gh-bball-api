# Generated by Django 4.2.4 on 2024-07-04 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_alter_game_game_number"),
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
                    ("SF1", "Semifinal 1"),
                    ("SF2", "Semifinal 2"),
                    ("F", "Final"),
                ],
                max_length=3,
                null=True,
            ),
        ),
    ]

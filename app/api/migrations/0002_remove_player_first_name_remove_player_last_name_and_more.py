# Generated by Django 4.2.4 on 2024-06-10 13:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="player",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="player",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="playerstatistics",
            name="points",
        ),
        migrations.RemoveField(
            model_name="playerstatistics",
            name="rebounds",
        ),
        migrations.AddField(
            model_name="game",
            name="game_number",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="jersey_number",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="name",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="position",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="blocks",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="defensive_rebounds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="fouls",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="free_throw_fg",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="offensive_rebounds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="steals",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="three_point_fg",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatistics",
            name="two_point_fg",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="team",
            name="hex_color",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="game",
            name="date",
            field=models.DateTimeField(null=True),
        ),
    ]

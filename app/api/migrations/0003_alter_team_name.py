# Generated by Django 4.2.4 on 2024-06-10 14:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_remove_player_first_name_remove_player_last_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

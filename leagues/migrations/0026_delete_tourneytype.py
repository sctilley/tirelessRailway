# Generated by Django 4.0.5 on 2022-11-23 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0025_remove_match_tourney_delete_tournament'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tourneytype',
        ),
    ]
# Generated by Django 4.0.5 on 2022-11-23 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0024_alter_match_tourney'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='tourney',
        ),
        migrations.DeleteModel(
            name='Tournament',
        ),
    ]

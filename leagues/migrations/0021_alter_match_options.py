# Generated by Django 4.0.5 on 2022-11-20 17:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0020_rename_tag_league_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'ordering': ['dateCreated', 'pk']},
        ),
    ]
# Generated by Django 4.0.5 on 2022-07-01 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0002_alter_archetype_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='flavor',
            name='isdefault',
            field=models.BooleanField(default=False, verbose_name='default'),
        ),
    ]

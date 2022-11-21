# Generated by Django 4.0.5 on 2022-11-21 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0022_alter_match_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flavor',
            name='deck',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='flavors', to='leagues.deck'),
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-06 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dataleakage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataleakfinding',
            name='is_user_blocked',
            field=models.BooleanField(default=False),
        ),
    ]

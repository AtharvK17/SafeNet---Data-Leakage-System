# Generated by Django 5.1.2 on 2024-10-28 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_profile_app_notifications_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics'),
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-22 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to='task_files/'),
        ),
    ]

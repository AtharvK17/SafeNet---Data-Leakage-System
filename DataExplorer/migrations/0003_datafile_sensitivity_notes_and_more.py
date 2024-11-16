# Generated by Django 5.1.2 on 2024-11-05 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataExplorer', '0002_datafile_user_alter_datafile_uploaded_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='sensitivity_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='datafile',
            name='sensitivity_score',
            field=models.FloatField(default=0.0),
        ),
    ]
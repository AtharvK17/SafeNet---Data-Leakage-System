# Generated by Django 5.1.2 on 2024-11-05 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataExplorer', '0003_datafile_sensitivity_notes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='findings',
            field=models.TextField(blank=True, null=True),
        ),
    ]

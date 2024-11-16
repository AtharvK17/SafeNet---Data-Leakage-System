# Projects models for the Projects app
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assigned_users = models.ManyToManyField(User, related_name='projects_assigned', blank=True)
    files = models.FileField(upload_to='project_files/', blank=True, null=True)  # Updated
    estimated_time = models.IntegerField(help_text='Estimated time in hours', blank=True, null=True)
    is_important = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    project_url = models.URLField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#ffffff')  # Assuming a hex color code
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')

    def __str__(self):
        return self.name

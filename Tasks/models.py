# Tasks models.py in the Task app
from django.db import models
from django.contrib.auth.models import User
from Notifications.models import Notification
from Projects.models import Project

class Task(models.Model):
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    files = models.FileField(upload_to='task_files/', blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_users = models.ManyToManyField(User)  # Using Django's default User model
    creator = models.ForeignKey(User, related_name="created_tasks", on_delete=models.SET_NULL, null=True)  # New field
    status = models.CharField(
        max_length=50,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold')
        ]
    )
    priority = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ]
    )
    estimated_time = models.PositiveIntegerField(help_text="Estimated time in hours")
    is_important = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    previous_status = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_task = Task.objects.get(pk=self.pk)
            if old_task.status != self.status:
                self.previous_status = old_task.status
                Notification.objects.create(
                    user=self.creator,  # Change if notifications are for assigned users
                    notification_type='task',
                    severity='info',
                    message=f'Task \"{self.task_name}\" status changed from \"{self.previous_status}\" to \"{self.get_status_display()}\"',
                    task=self
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.task_name

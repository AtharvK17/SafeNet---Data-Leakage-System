# Notifications models for the Notifications app
from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    SEVERITY_LEVELS = [
        ('danger', 'Danger'),
        ('leak', 'Leak'),
        ('success', 'Success'),
        ('normal', 'Normal'),
        ('info', 'Info'),
        ('warning', 'Warning'),
    ]

    NOTIFICATION_TYPES = [
        ('project', 'Project'),
        ('task', 'Task'),
        ('data_leak', 'Data Leakage'),
        ('account', 'Account'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('system', 'System'),  # For system-level notifications
        ('reminder', 'Reminder'),  # For reminders
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional Foreign Keys for linking notifications to projects or tasks
    project = models.ForeignKey('Projects.Project', null=True, blank=True, on_delete=models.SET_NULL)
    task = models.ForeignKey('Tasks.Task', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.severity}: {self.message}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @classmethod
    def unread_notifications(cls, user):
        return cls.objects.filter(user=user, is_read=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-timestamp']

# projects/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Project
from Notifications.models import Notification


@receiver(post_save, sender=Project)
def create_project_notification(sender, instance, created, **kwargs):
    """
    Create notifications when a project is created or updated
    """
    if created:
        # Notify all assigned users about new project
        for user in instance.assigned_users.all():
            Notification.objects.create(
                user=user,
                notification_type='project',
                severity='info',
                message=f'You have been assigned to a new project: {instance.name}'
            )

        # Notify creator about successful project creation
        Notification.objects.create(
            user=instance.creator,
            notification_type='project',
            severity='success',
            message=f'Project "{instance.name}" was created successfully'
        )
    else:
        # Notify relevant users about project updates
        for user in instance.assigned_users.all():
            Notification.objects.create(
                user=user,
                notification_type='project',
                severity='info',
                message=f'Project "{instance.name}" has been updated'
            )


@receiver(post_delete, sender=Project)
def delete_project_notification(sender, instance, **kwargs):
    """
    Create notifications when a project is deleted
    """
    # Notify all previously assigned users about project deletion
    for user in instance.assigned_users.all():
        Notification.objects.create(
            user=user,
            notification_type='project',
            severity='warning',
            message=f'Project "{instance.name}" has been deleted'
        )

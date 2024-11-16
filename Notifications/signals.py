from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from Projects.models import Project
from Tasks.models import Task


@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    if created:
        # Send a notification when a task is created
        Notification.objects.create(
            user=instance.assigned_to,  # Or whichever user you want to notify
            notification_type='task',
            severity='info',
            message=f"A new task '{instance.name}' has been assigned to you.",
        )


@receiver(post_save, sender=Project)
def project_notification(sender, instance, created, **kwargs):
    if created:
        # Send a notification when a project is created
        Notification.objects.create(
            user=instance.owner,  # Or whichever user you want to notify
            notification_type='project',
            severity='success',
            message=f"A new project '{instance.name}' has been created.",
        )

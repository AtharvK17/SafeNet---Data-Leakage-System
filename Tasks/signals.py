from django.db.models.signals import post_save, post_delete, m2m_changed, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task
from Notifications.models import Notification


def create_task_notification(task, user, action):
    """Helper function to create notifications for task events"""
    message = {
        'created': f'You have been assigned to a new task: {task.task_name}',
        'updated': f'Task "{task.task_name}" has been updated',
        'deleted': f'Task "{task.task_name}" has been deleted',
        'status_changed': f'Status of task "{task.task_name}" has been changed to {task.status}',
        'assigned': f'You have been assigned to task: {task.task_name}',
        'unassigned': f'You have been unassigned from task: {task.task_name}'
    }.get(action)

    if message:
        Notification.objects.create(
            user=user,  # The user receiving the notification
            notification_type='task',  # Notification type for task-related events
            severity='info',  # Default severity; you can adjust this based on the action if needed
            message=message,
            task=task  # Link the notification to the task
        )


# Store the old status before save
@receiver(pre_save, sender=Task)
def store_old_status(sender, instance, **kwargs):
    try:
        instance._old_status = Task.objects.get(pk=instance.pk).status
    except Task.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Signal to handle task creation and updates"""
    if created:
        # Notify all assigned users about the new task
        for user in instance.assigned_users.all():
            create_task_notification(instance, user, 'created')
    else:
        # Check if status has changed by comparing with stored old status
        old_status = getattr(instance, '_old_status', None)
        if old_status is not None and old_status != instance.status:
            for user in instance.assigned_users.all():
                create_task_notification(instance, user, 'status_changed')
        # Notify about general updates
        else:
            for user in instance.assigned_users.all():
                create_task_notification(instance, user, 'updated')


@receiver(post_delete, sender=Task)
def task_post_delete(sender, instance, **kwargs):
    """Signal to handle task deletion"""
    for user in instance.assigned_users.all():
        create_task_notification(instance, user, 'deleted')


@receiver(m2m_changed, sender=Task.assigned_users.through)
def task_users_changed(sender, instance, action, pk_set, **kwargs):
    """Signal to handle changes in task assignments"""
    if action == "post_add":
        # Notify newly assigned users
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            create_task_notification(instance, user, 'assigned')

    elif action == "post_remove":
        # Notify removed users
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            create_task_notification(instance, user, 'unassigned')

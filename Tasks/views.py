#Task views
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Accounts.models import Profile
from .models import Task
from .forms import TaskForm
from Notifications.models import Notification
from Accounts.models import UserActivityLog  # Ensure this is imported

@login_required
def task_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    tasks = Task.objects.filter(assigned_users=request.user)
    return render(request, 'Tasks/Task.html', {'tasks': tasks, 'profile': profile})

@login_required
def create_task(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            task.save()
            form.save_m2m()  # Save assigned users

            # Create a notification for each assigned user
            for user in task.assigned_users.all():
                Notification.objects.create(
                    user=user,
                    notification_type='task',
                    severity='info',
                    message=f'You have been assigned to the new task: {task.task_name}',
                    task=task
                )

            messages.success(request, 'Task created and notifications sent successfully!')

            # Log task creation activity
            UserActivityLog.objects.create(
                user=request.user,
                action='Created task',
                details=f'User {request.user.username} created task "{task.task_name}".'
            )

            return redirect('tasks:task_list')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = TaskForm()

    return render(request, 'Tasks/Create-tasks.html', {'form': form, 'profile': profile})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.user != task.creator:
        return HttpResponseForbidden("You do not have permission to edit this task.")

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, 'Task updated successfully!')

            # Notify assigned users of the update
            for user in updated_task.assigned_users.all():
                Notification.objects.create(
                    user=user,
                    notification_type='task',
                    severity='info',
                    message=f'Task "{updated_task.task_name}" has been updated.',
                    task=updated_task
                )

            # Log task update activity
            UserActivityLog.objects.create(
                user=request.user,
                action='Updated task',
                details=f'User {request.user.username} updated task "{updated_task.task_name}".'
            )

            return redirect('tasks:task_list')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = TaskForm(instance=task)

    return render(request, 'Tasks/Edit-task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, id=task_id)
            task_name = task.task_name
            assigned_users = list(task.assigned_users.all())
            
            task.delete()

            # Create notifications for assigned users
            for user in assigned_users:
                Notification.objects.create(
                    user=user,
                    notification_type='task',
                    severity='danger',
                    message=f'Task "{task_name}" has been deleted.'
                )

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='Deleted task',
                details=f'User {request.user.username} deleted task "{task_name}".'
            )

            return JsonResponse({'success': True, 'message': 'Task deleted successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

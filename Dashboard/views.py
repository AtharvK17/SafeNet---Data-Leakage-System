# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from Projects.models import Project
from Tasks.models import Task
from Notifications.models import Notification
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


@login_required
def dashboard(request):
    # Get current user
    user = request.user
    active_users_count = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()

    # Calculate KPIs
    total_projects = Project.objects.filter(assigned_users=user).count()
    total_tasks = Task.objects.filter(assigned_users=user).count()

    # Calculate month-over-month project growth
    last_month = timezone.now() - timedelta(days=30)
    projects_last_month = Project.objects.filter(
        assigned_users=user,
        start_date__lt=last_month
    ).count()

    if projects_last_month > 0:
        project_growth = ((total_projects - projects_last_month) / projects_last_month) * 100
    else:
        project_growth = 100

    # Calculate task growth
    tasks_last_month = Task.objects.filter(
        assigned_users=user,
        start_date__lt=last_month
    ).count()

    if tasks_last_month > 0:
        task_growth = ((total_tasks - tasks_last_month) / tasks_last_month) * 100
    else:
        task_growth = 100

    # Get recent alerts
    recent_alerts = Notification.objects.filter(
        user=user
    ).order_by('-timestamp')[:3]

    # Get all projects assigned to the user
    all_projects = Project.objects.filter(assigned_users=user).order_by('-start_date')

    # Calculate project progress for each project
    for project in all_projects:
        total_tasks = Task.objects.filter(project=project).count()
        completed_tasks = Task.objects.filter(
            project=project,
            status='completed'
        ).count()
        project.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Get upcoming tasks
    upcoming_tasks = Task.objects.filter(
        assigned_users=user,
        status__in=['not_started', 'in_progress'],
        end_date__gte=timezone.now()
    ).order_by('end_date')[:3]

    # Calculate safety score
    total_leaks = Notification.objects.filter(
        user=user,
        notification_type='data_leak'
    ).count()

    minor_leaks = Notification.objects.filter(
        user=user,
        notification_type='data_leak',
        severity='info'
    ).count()

    moderate_leaks = Notification.objects.filter(
        user=user,
        notification_type='data_leak',
        severity='warning'
    ).count()

    severe_leaks = Notification.objects.filter(
        user=user,
        notification_type='data_leak',
        severity='danger'
    ).count()


    minor_leaks = 1
    moderate_leaks = 0
    severe_leaks = 1
    # Calculate safety score (100 - deductions)
    safety_score = 100 - (minor_leaks * 5 + moderate_leaks * 15 + severe_leaks * 30)
    safety_score = max(0, min(100, safety_score))

    # Get project timeline data
    projects_timeline = Project.objects.filter(
        assigned_users=user
    ).values('name', 'start_date', 'end_date', 'status')[:10]

    # Get user's profile
    user_profile = request.user.profile
    
    # Determine safety status and badge color based on sensitivity score
    sensitivity_score = user_profile.sensitivity_score
    if sensitivity_score >= 80:
        safety_status = "High Risk"
        safety_badge = "danger"
    elif sensitivity_score >= 50:
        safety_status = "Medium Risk"
        safety_badge = "warning"
    else:
        safety_status = "Low Risk"
        safety_badge = "success"

    # Get total users count
    total_users = User.objects.count()
    
    # Get users who joined in the last 30 days
    new_users = User.objects.filter(date_joined__gte=last_month).count()
    
    # Calculate user growth percentage
    previous_month_users = User.objects.filter(
        date_joined__lt=last_month
    ).count()
    
    user_growth = (
        ((new_users - previous_month_users) / previous_month_users * 100)
        if previous_month_users > 0 else 0
    )

    context = {
        'user': user,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'project_growth': project_growth,
        'task_growth': task_growth,
        'recent_alerts': recent_alerts,
        'active_users': active_users_count,  # Make sure this is defined
        'all_projects': all_projects,
        'upcoming_tasks': upcoming_tasks,
        'safety_score': safety_score,
        'minor_leaks': minor_leaks,
        'moderate_leaks': moderate_leaks,
        'severe_leaks': severe_leaks,
        'projects_timeline': projects_timeline,
        'safety_status': safety_status,
        'safety_badge': safety_badge,
        'total_users': total_users,
        'new_users': new_users,
        'user_growth': user_growth,
    }

    return render(request, 'Dashboard/dashboard.html', context)

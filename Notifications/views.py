from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification
from Accounts.models import Profile  # Import Profile model
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def notification_settings(request):
    notifications = Notification.unread_notifications(request.user)
    profile = get_object_or_404(Profile, user=request.user)  # Use get_object_or_404 for better error handling

    if request.method == 'POST':
        # Get preferences from the form
        profile.email_notifications = request.POST.get('email_notifications', 'off') == 'on'
        profile.browser_notifications = request.POST.get('browser_notifications', 'off') == 'on'
        profile.app_notifications = request.POST.get('app_notifications', 'off') == 'on'

        # Save the profile with updated preferences
        profile.save()
        messages.success(request, 'Notification preferences updated successfully!')  # Add a success message

        return redirect('landing')  # Change to your URL name

    context = {
        'notifications': notifications,
        'profile': profile,  # Pass profile to the context
    }
    return render(request, 'Accounts/Account-settings-notifications.html', context)


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification_list.html', context)

@require_POST
@login_required
def mark_as_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = not notification.is_read  # Toggle read status
        notification.save()
        return JsonResponse({
            'success': True,
            'is_read': notification.is_read,
            'message': f'Notification marked as {"read" if notification.is_read else "unread"}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_POST
@login_required
def mark_all_read(request):
    try:
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({
            'success': True,
            'message': f'{updated} notifications marked as read'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_POST
@login_required
def delete_notification(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_POST
@login_required
def delete_all_notifications(request):
    try:
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({
            'success': True,
            'message': 'All notifications cleared'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def unread_notifications(request):
    notifications = Notification.unread_notifications(request.user)
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/unread_notifications.html', context)


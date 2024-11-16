from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('settings/', views.notification_settings, name='notification_settings'),
    path('', views.notification_list, name='notification_list'),
    path('mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('delete-all/', views.delete_all_notifications, name='delete_all'),
    path('unread/', views.unread_notifications, name='unread_notifications'),
]

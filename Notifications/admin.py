from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'severity', 'is_read', 'timestamp')
    list_filter = ('user', 'notification_type', 'severity', 'is_read')
    search_fields = ('message',)


admin.site.register(Notification, NotificationAdmin)

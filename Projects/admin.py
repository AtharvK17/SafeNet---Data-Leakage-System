from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Display fields in the list view in tabulated format
    list_display = (
        'name', 'description', 'start_date', 'end_date', 'status', 'priority',
        'assigned_users_display', 'files', 'estimated_time', 'is_important_display',
        'comments', 'email_notifications', 'sms_notifications', 'color'
    )

    # Enable search functionality for name and description
    search_fields = ('name', 'description')

    # Filter by status, priority, and dates
    list_filter = ('status', 'priority', 'start_date', 'end_date')

    # Group fields in a tabulated format in the admin detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Dates & Status', {
            'fields': ('start_date', 'end_date', 'status', 'priority')
        }),
        ('Assignment & Files', {
            'fields': ('assigned_users', 'files')
        }),
        ('Additional Information', {
            'fields': ('estimated_time', 'is_important', 'comments')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Visual', {
            'fields': ('color',)
        }),
    )

    # Customize the display of assigned users
    def assigned_users_display(self, obj):
        return ", ".join([user.username for user in obj.assigned_users.all()])

    assigned_users_display.short_description = 'Assigned Users'

    # Customize the display of whether the project is important
    def is_important_display(self, obj):
        return "✔️" if obj.is_important else "❌"  # Display checkmark for important projects

    is_important_display.short_description = 'Important'
    is_important_display.admin_order_field = 'is_important'  # Allows sorting by this field

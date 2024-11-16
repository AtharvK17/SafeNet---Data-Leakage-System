from django.contrib import admin
from .models import Profile, UserActivityLog, BlockedUser


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'organization',
        'country',
        'sensitivity_score',
        'user_status',  # Changed from is_blocked
    )
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_filter = ('country', 'user__is_active')  # Changed from is_blocked
    ordering = ('user',)

    # Optional: Customize detail view layout
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'organization', 'country', 'profile_picture', 'date_of_birth', 'sensitivity_score')
        }),
    )

    # Optional: Add functionality for making the profile active/inactive
    actions = ['activate_profiles', 'deactivate_profiles']

    def activate_profiles(self, request, queryset):
        queryset.update(is_active=True)  # Assume you have an `is_active` field
        self.message_user(request, "Selected profiles have been activated.")

    def deactivate_profiles(self, request, queryset):
        queryset.update(is_active=False)  # Assume you have an `is_active` field
        self.message_user(request, "Selected profiles have been deactivated.")

    activate_profiles.short_description = "Activate selected profiles"
    deactivate_profiles.short_description = "Deactivate selected profiles"

    def user_status(self, obj):
        return 'Blocked' if not obj.user.is_active else 'Active'
    user_status.short_description = 'Status'


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    # Define the columns to display in the table
    list_display = (
        'user',  # Display the username
        'action',  # Action taken by the user
        'timestamp',  # Time when the action occurred
        'details',  # Additional details of the action
    )
    # Add search functionality to search logs by action or user
    search_fields = ('user__username', 'action', 'details')
    # Filter options by action and timestamp
    list_filter = ('action', 'timestamp')
    # Allow sorting by timestamp
    ordering = ('-timestamp',)  # Sort by timestamp in descending order

    # Optional: You can also customize the detail view layout for this model
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'timestamp', 'details')
        }),
    )

# Optional: Register the other models
try:
    admin.site.register(UserActivityLog)
except admin.sites.AlreadyRegistered:
    pass
admin.site.register(BlockedUser)

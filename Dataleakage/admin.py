# Dataleakage/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import DataLeakFinding
from Accounts.models import Profile  # Import Profile model for linked info


class DataLeakFindingAdmin(admin.ModelAdmin):
    # Define the columns to be displayed in the table view
    list_display = (
        'user',
        'file_name',
        'matched_content_excerpt',  # Show a snippet of the matched content
        'sensitivity_level',
        'risk_score',
        'detection_time',
        'is_user_blocked',
        'view_user_profile'
    )

    # Filters available for the admin table
    list_filter = ('sensitivity_level', 'is_user_blocked')
    # Add a search bar that allows searching by file name or matched content
    search_fields = ('file_name', 'matched_content')

    # Enables sorting by detection time
    date_hierarchy = 'detection_time'

    # Default ordering of the table (descending detection time)
    ordering = ('-detection_time',)

    # Add a method to show an excerpt of matched content (first 50 chars)
    def matched_content_excerpt(self, obj):
        return f"{obj.matched_content[:50]}..." if len(obj.matched_content) > 50 else obj.matched_content
    matched_content_excerpt.short_description = 'Matched Content'  # Set column name

    # Create a custom link to view the user's profile
    def view_user_profile(self, obj):
        return format_html('<a href="/admin/Accounts/profile/{}/change/">View Profile</a>', obj.user.profile.id)
    view_user_profile.short_description = 'User Profile'

    # Add more user-related fields, like 'is_blocked' status
    def user_blocked_status(self, obj):
        return obj.user.profile.is_blocked  # Access the user's profile and blocked status directly
    user_blocked_status.short_description = 'User Blocked'

# Register the model with the custom admin configuration
admin.site.register(DataLeakFinding, DataLeakFindingAdmin)

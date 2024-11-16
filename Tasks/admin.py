# admin.py in the Task app
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'start_date', 'end_date', 'status', 'priority', 'is_important']
    list_filter = ['status', 'priority', 'is_important']
    search_fields = ['task_name', 'description']

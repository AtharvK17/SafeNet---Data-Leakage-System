# admin.py
from django.contrib import admin
from .models import DataFile, DataVisualization


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_by', 'uploaded_at', 'last_modified', 'rounded_sensitivity_score')
    search_fields = ('title', 'uploaded_by__username', 'file_type')
    list_filter = ('file_type', 'uploaded_at', 'last_modified')
    readonly_fields = ('uploaded_at', 'last_modified')
    ordering = ('-uploaded_at',)

    def rounded_sensitivity_score(self, obj):
        """Returns the sensitivity score rounded to 2 decimal places."""
        return f"{obj.sensitivity_score:.2f}"  # Format to 2 decimal places
    rounded_sensitivity_score.short_description = 'Sensitivity Score'


@admin.register(DataVisualization)
class DataVisualizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'data_file', 'chart_type', 'created_by', 'created_at')
    search_fields = ('title', 'chart_type', 'created_by__username', 'data_file__title')
    list_filter = ('chart_type', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

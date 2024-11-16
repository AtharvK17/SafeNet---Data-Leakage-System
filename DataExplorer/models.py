from django.db import models
from django.contrib.auth.models import User

class DataFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='data_files/')  # Creates a folder called 'data_files' inside your media folder
    file_type = models.CharField(max_length=10)  # e.g., csv, xlsx
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_files')

    # New fields for sensitivity score and findings
    sensitivity_score = models.FloatField(default=0.0)  # Sensitivity score, default to 0.0
    sensitivity_notes = models.TextField(blank=True, null=True)  # Notes on why the score was given
    findings = models.TextField(blank=True, null=True)  # Detailed findings from the sensitivity analysis

    def get_uploader_initials(self):
        """Returns the initials of the uploader."""
        full_name = self.uploaded_by.get_full_name()
        if full_name:
            return ''.join(name[0].upper() for name in full_name.split())
        return self.uploaded_by.username[:2].upper()

    def __str__(self):
        return self.title

class DataVisualization(models.Model):
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('scatter', 'Scatter Plot'),
    ]

    title = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    x_axis = models.CharField(max_length=100)
    y_axis = models.CharField(max_length=100)
    data_file = models.ForeignKey(DataFile, on_delete=models.CASCADE)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    configuration = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.title} - {self.chart_type}"

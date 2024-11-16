# forms.py
from django import forms
from .models import DataLeakFinding  # Import your model


class DataLeakFindingForm(forms.ModelForm):
    class Meta:
        model = DataLeakFinding
        fields = ['user', 'file_name', 'matched_content', 'sensitivity_level', 'risk_score', 'is_user_blocked']
        widgets = {
            'matched_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'user': 'User',
            'file_name': 'File Name',
            'matched_content': 'Matched Content',
            'sensitivity_level': 'Sensitivity Level',
            'risk_score': 'Risk Score',
            'is_user_blocked': 'Is User Blocked',
        }

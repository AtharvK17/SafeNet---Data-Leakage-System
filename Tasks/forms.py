# forms.py
from django import forms  # Ensure this line is included
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Assign Users"
    )

    class Meta:
        model = Task
        fields = [
            'task_name', 'description', 'start_date', 'end_date', 'project',
            'assigned_users', 'status', 'priority', 'estimated_time',
            'is_important', 'comments', 'email_notifications', 'sms_notifications', 'files'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add classes and attributes to form fields
        self.fields['task_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Task Name',
            'required': True
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Task Description',
            'style': 'height: 100px',
            'required': True
        })
        self.fields['start_date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': True
        })
        self.fields['end_date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': True
        })
        self.fields['status'].widget.attrs.update({
            'class': 'form-select',
            'required': True
        })
        self.fields['priority'].widget.attrs.update({
            'class': 'form-select',
            'required': True
        })
        self.fields['project'].widget.attrs.update({
            'class': 'form-select'
        })

        # Check if 'files' field exists in the form before updating its attributes
        if 'files' in self.fields:
            self.fields['files'].widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['estimated_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Estimated Time'
        })
        self.fields['is_important'].widget.attrs.update({
            'class': 'form-check-input'
        })
        self.fields['comments'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Comments or Notes',
            'style': 'height: 100px'
        })
        self.fields['email_notifications'].widget.attrs.update({
            'class': 'form-check-input'
        })
        self.fields['sms_notifications'].widget.attrs.update({
            'class': 'form-check-input'
        })

from django import forms
from .models import Project
from django.contrib.auth.models import User  # Correct import


class ProjectForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),  # Corrected line
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Assign Users"
    )

    class Meta:
        model = Project
        fields = [
            'name', 'description', 'start_date', 'end_date', 'status', 'priority',
            'assigned_users', 'files', 'estimated_time', 'is_important',
            'comments', 'email_notifications', 'sms_notifications', 'color'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add classes and attributes to form fields
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Project Name',
            'required': True
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Project Description',
            'style': 'height: 100px',
            'required': True
        })

        # Use DateInput for date fields
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

        # Update select fields
        self.fields['status'].widget.attrs.update({
            'class': 'form-select',
            'required': True
        })
        self.fields['priority'].widget.attrs.update({
            'class': 'form-select',
            'required': True
        })

        # Other fields
        self.fields['files'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['estimated_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Estimated Time'
        })
        # Important field configuration
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
        self.fields['color'].widget = forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-color'
        })
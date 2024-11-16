from django import forms
from .models import Notification


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['notification_type', 'severity', 'message']

        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

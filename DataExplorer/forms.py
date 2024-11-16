# forms.py
from django import forms
from .models import DataFile, DataVisualization


class DataFileForm(forms.ModelForm):
    class Meta:
        model = DataFile
        fields = ['file']


class DataVisualizationForm(forms.ModelForm):
    class Meta:
        model = DataVisualization
        fields = ['title', 'chart_type', 'x_axis', 'y_axis']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'chart_type': forms.Select(attrs={'class': 'form-control'}),
            'x_axis': forms.Select(attrs={'class': 'form-control'}),
            'y_axis': forms.Select(attrs={'class': 'form-control'}),
        }

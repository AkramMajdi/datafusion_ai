from django import forms
from .models import DataSource


class UploadFileForm(forms.ModelForm):
    class Meta:
        model  = DataSource
        fields = ['name', 'source_type', 'file', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Telecom Marketing Dataset Q1 2025',
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls,.csv',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...',
            }),
        }
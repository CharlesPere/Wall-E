from django import forms
from .models import Intervention


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['robot_type', 'robot_count', 'worker_count', 'resources', 'estimated_hours', 'comment']
        widgets = {
            'resources': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 2}),
            'estimated_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'}),
        }

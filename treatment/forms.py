from django import forms
from .models import Intervention


class InterventionForm(forms.ModelForm):
    def __init__(self, *args, allow_multipurpose=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Multipurpose robots are only available after a natural disaster
        if not allow_multipurpose:
            self.fields['robot_type'].choices = [
                c for c in self.fields['robot_type'].choices if c[0] != 'multipurpose'
            ]

    class Meta:
        model = Intervention
        fields = ['robot_type', 'robot_count', 'worker_count', 'resources', 'estimated_hours', 'comment']
        widgets = {
            'resources': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 2}),
            'estimated_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'}),
        }

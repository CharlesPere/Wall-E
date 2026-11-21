from django import forms
from .models import Intervention


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['type_robot', 'nb_robots', 'nb_ouvriers', 'ressources', 'temps_estime', 'commentaire']
        widgets = {
            'ressources': forms.Textarea(attrs={'rows': 3}),
            'commentaire': forms.Textarea(attrs={'rows': 2}),
            'temps_estime': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'}),
        }

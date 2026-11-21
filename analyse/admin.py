from django.contrib import admin
from .models import Mesure, Rapport


@admin.register(Mesure)
class MesureAdmin(admin.ModelAdmin):
    list_display = ('zone', 'date', 'temperature', 'humidite', 'oxygene', 'co2')
    list_filter = ('zone',)


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('titre', 'zone', 'niveau_risque', 'date_analyse', 'auteur')
    list_filter = ('niveau_risque', 'zone')

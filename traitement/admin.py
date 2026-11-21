from django.contrib import admin
from .models import Intervention


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ('zone', 'type_robot', 'nb_robots', 'nb_ouvriers', 'temps_estime', 'statut', 'date_creation')
    list_filter = ('statut', 'type_robot', 'zone')

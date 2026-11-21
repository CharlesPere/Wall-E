from django.urls import path
from . import views

urlpatterns = [
    path('zone/<int:pk>/traitement/', views.zone_traitement, name='zone-traitement'),
    path('intervention/<int:pk>/avancer/', views.intervention_avancer, name='intervention-avancer'),
    path('intervention/<int:pk>/supprimer/', views.intervention_supprimer, name='intervention-supprimer'),
]

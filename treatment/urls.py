from django.urls import path
from . import views

urlpatterns = [
    path('zone/<int:pk>/treatment/', views.zone_treatment, name='zone-treatment'),
    path('intervention/<int:pk>/advance/', views.intervention_advance, name='intervention-advance'),
    path('intervention/<int:pk>/delete/', views.intervention_delete, name='intervention-delete'),
]

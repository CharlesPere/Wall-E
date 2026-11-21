from django.urls import path
from . import views

urlpatterns = [
    path('zone/<int:pk>/analyse/', views.zone_analyse, name='zone-analyse'),
    path('zone/<int:pk>/analyse/lancer/', views.lancer_analyse, name='zone-lancer-analyse'),
    path('zone/<int:pk>/rapport/new/', views.RapportCreateView.as_view(), name='rapport-create'),
    path('rapport/<int:pk>/', views.RapportDetailView.as_view(), name='rapport-detail'),
    path('rapport/<int:pk>/update/', views.RapportUpdateView.as_view(), name='rapport-update'),
    path('rapport/<int:pk>/delete/', views.RapportDeleteView.as_view(), name='rapport-delete'),
]

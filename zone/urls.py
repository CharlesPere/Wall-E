from django.urls import path
from .views import (
    ZoneListView,
    ZoneDetailView,
    ZoneCreateView,
    ZoneUpdateView,
    ZoneDeleteView
)
from . import views

urlpatterns = [
    path('', ZoneListView.as_view(), name='zone-home'),
    path('zone/<int:pk>/', ZoneDetailView.as_view(), name='zone-detail'),
    path('zone/new/', ZoneCreateView.as_view(), name='zone-create'),
    path('zone/<int:pk>/update/', ZoneUpdateView.as_view(), name='zone-update'),
    path('zone/<int:pk>/delete/', ZoneDeleteView.as_view(), name='zone-delete'),
    path('about/', views.about, name='zone-about'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('zone/<int:pk>/analysis/', views.zone_analysis, name='zone-analysis'),
    path('zone/<int:pk>/analysis/run/', views.run_analysis, name='zone-run-analysis'),
    path('zone/<int:pk>/report/new/', views.ReportCreateView.as_view(), name='report-create'),
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('report/<int:pk>/update/', views.ReportUpdateView.as_view(), name='report-update'),
    path('report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report-delete'),
]

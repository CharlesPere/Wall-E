from django.contrib import admin
from .models import Intervention


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ('zone', 'robot_type', 'robot_count', 'worker_count', 'estimated_hours', 'status', 'created_at')
    list_filter = ('status', 'robot_type', 'zone')

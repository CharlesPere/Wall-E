from django.contrib import admin
from .models import FarmMeasurement, Measurement, Report


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('zone', 'date', 'temperature', 'humidity', 'oxygen', 'co2')
    list_filter = ('zone',)


@admin.register(FarmMeasurement)
class FarmMeasurementAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'yield_percent', 'harvest_state', 'needs_fertilizer')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'zone', 'risk_level', 'analysis_date', 'author')
    list_filter = ('risk_level', 'zone')

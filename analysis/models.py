from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from zone.models import Zone

# Thresholds
MAX_TEMPERATURE = 40   # °C  (above => fire risk)
MIN_HUMIDITY = 20      # %   (below => drought)
MIN_OXYGEN = 18        # %   (below => low oxygen)
MAX_CO2 = 1000         # ppm (above => air pollution)

# Zone types that have extra farming stats
FARM_TYPES = ['AGRICULTURE_FIELD', 'ORCHARD']

RISK_LEVELS = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


def is_farm(zone):
    return zone.type_area in FARM_TYPES


class Measurement(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='measurements')
    date = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField()
    humidity = models.FloatField()
    oxygen = models.FloatField()
    co2 = models.FloatField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.zone.name_zone} - {self.date:%d/%m/%Y %H:%M}"

    def alerts(self):
        alerts = []
        if self.temperature > MAX_TEMPERATURE:
            alerts.append("Fire risk")
        if self.humidity < MIN_HUMIDITY:
            alerts.append("Drought")
        if self.oxygen < MIN_OXYGEN:
            alerts.append("Low oxygen")
        if self.co2 > MAX_CO2:
            alerts.append("Air pollution")
        return alerts

    def risk_level(self):
        count = len(self.alerts())
        if count == 0:
            return 'low'
        if count == 1:
            return 'medium'
        if count == 2:
            return 'high'
        return 'critical'

    def risk_label(self):
        return dict(RISK_LEVELS)[self.risk_level()]

    def farm_alerts(self):
        farm = getattr(self, 'farm', None)
        return farm.alerts() if farm else []


class FarmMeasurement(models.Model):
    """Extra stats for farming zones, linked to a measurement."""
    HARVEST_STATES = [
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ]

    measurement = models.OneToOneField(Measurement, on_delete=models.CASCADE, related_name='farm')
    yield_percent = models.FloatField()       # % of expected yield
    harvest_state = models.CharField(max_length=10, choices=HARVEST_STATES)
    needs_fertilizer = models.BooleanField(default=False)

    def __str__(self):
        return f"Farm - {self.measurement}"

    def alerts(self):
        """[(problem, color level)]"""
        alerts = []
        if self.harvest_state == 'poor':
            alerts.append(("Poor harvest", 'high'))
        if self.needs_fertilizer:
            alerts.append(("Needs fertilizer", 'medium'))
        return alerts

    @property
    def state_badge(self):
        return {'good': 'risk-badge-low', 'average': 'risk-badge-medium',
                'poor': 'risk-badge-high'}[self.harvest_state]


class Report(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='reports')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    analysis_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-analysis_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('report-detail', kwargs={'pk': self.pk})

    @property
    def risk_badge(self):
        return f"risk-badge-{self.risk_level}"

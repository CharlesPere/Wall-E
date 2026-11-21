from django.db import models
from django.contrib.auth.models import User
from zone.models import Zone


class Intervention(models.Model):
    ROBOT_TYPES = [
        ('firefighter', "Firefighter robot (fire)"),
        ('irrigation', "Irrigation robot (drought)"),
        ('oxygenation', "Oxygenation robot (low oxygen)"),
        ('filtration', "Filtration robot (pollution)"),
        ('farming', "Farming robot (harvest / fertilizer)"),
        ('multipurpose', "Multipurpose robot"),
    ]
    STATUSES = [
        ('planned', 'Planned'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
    ]

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='interventions')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    robot_type = models.CharField("Robot type", max_length=20, choices=ROBOT_TYPES)
    robot_count = models.PositiveIntegerField("Number of robots", default=1)
    worker_count = models.PositiveIntegerField("Number of workers", default=0)
    resources = models.TextField("Required resources", blank=True,
                                 help_text="E.g. 2000 L of water, 3 filters, 1 generator…")
    estimated_hours = models.FloatField("Estimated time (hours)")
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    # problems this intervention treats (comma-separated, snapshot at creation)
    problems = models.TextField(blank=True)
    # number of upcoming analyses during which these problems cannot come back
    immunity_runs = models.PositiveIntegerField(default=0)

    IMMUNITY_RUNS = 2

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_robot_type_display()} - {self.zone.name_zone}"

    @property
    def started_ms(self):
        """Start time in milliseconds (for the progress bar)."""
        return int(self.started_at.timestamp() * 1000) if self.started_at else 0

    @property
    def duration_seconds(self):
        """Simulation: 1 estimated hour = 1 real second."""
        return self.estimated_hours

    def problem_list(self):
        return [p.strip() for p in self.problems.split(',') if p.strip()]

    @property
    def status_badge(self):
        return {'planned': 'secondary', 'in_progress': 'warning', 'done': 'success'}.get(self.status, 'secondary')

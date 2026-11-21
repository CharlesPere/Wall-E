from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Zone(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ANALYSIS", "Under analysis"),
        ("SUSPENDED", "Suspended"),
    ]

    TYPE_EREA = [
        ("WOODS", "Woods"),
        ("RIVER", "River"),
        ("MEADOW", "Meadow"),
        ("AGRICULTURE_FIELD", "Agriculture field")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name_zone = models.CharField(max_length=100)

    localisation = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    size_zone = models.FloatField(
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    type_area = models.CharField(
        max_length=20, 
        choices=TYPE_EREA,
        default="WOODS"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def get_absolute_url(self):
        return reverse('zone-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.user


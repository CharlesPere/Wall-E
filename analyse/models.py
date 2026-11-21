from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from zone.models import Zone

# Seuils du cahier des charges
SEUIL_TEMPERATURE = 40   # °C  (au-dessus => risque incendie)
SEUIL_HUMIDITE = 20      # %   (en dessous => sécheresse)
SEUIL_OXYGENE = 18       # %   (en dessous => manque d'oxygène)
SEUIL_CO2 = 1000         # ppm (au-dessus => pollution)


class Mesure(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='mesures')
    date = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField()
    humidite = models.FloatField()
    oxygene = models.FloatField()
    co2 = models.FloatField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.zone.name_zone} - {self.date:%d/%m/%Y %H:%M}"

    def alertes(self):
        alertes = []
        if self.temperature > SEUIL_TEMPERATURE:
            alertes.append("Risque incendie")
        if self.humidite < SEUIL_HUMIDITE:
            alertes.append("Sécheresse")
        if self.oxygene < SEUIL_OXYGENE:
            alertes.append("Manque d'oxygène")
        if self.co2 > SEUIL_CO2:
            alertes.append("Pollution atmosphérique")
        return alertes

    def niveau_risque(self):
        n = len(self.alertes())
        if n == 0:
            return 'faible'
        if n == 1:
            return 'moyen'
        if n == 2:
            return 'eleve'
        return 'critique'


class Rapport(models.Model):
    NIVEAUX_RISQUE = [
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('eleve', 'Élevé'),
        ('critique', 'Critique'),
    ]

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='rapports')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    contenu = models.TextField()
    niveau_risque = models.CharField(max_length=10, choices=NIVEAUX_RISQUE, default='faible')
    date_analyse = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_analyse']

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('rapport-detail', kwargs={'pk': self.pk})

    @property
    def badge_risque(self):
        return {
            'faible': 'success',
            'moyen': 'warning',
            'eleve': 'danger',
            'critique': 'dark',
        }.get(self.niveau_risque, 'secondary')
